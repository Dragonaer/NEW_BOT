from __future__ import annotations

import html
import os
from pathlib import Path

import telebot
from telebot import types

from kanban.domain.models import Status
from kanban.service.task_service import TaskNotFoundError, TaskService, ValidationError
from kanban.storage.json_store import JsonStore


STATUS_LABELS = {
    Status.TODO: "ToDo",
    Status.IN_PROGRESS: "InProgress",
    Status.DONE: "Done",
}

STATUS_TITLES = {
    Status.TODO: "ToDo",
    Status.IN_PROGRESS: "In Progress",
    Status.DONE: "Done",
}


from dotenv import load_dotenv
load_dotenv()

def _get_token() -> str:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Set BOT_TOKEN environment variable")
    return token


store = JsonStore(Path("data") / "kanban.json")
task_service = TaskService(store)
bot = telebot.TeleBot(_get_token(), parse_mode="HTML")


def _status_keyboard(task_id: int) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [
        types.InlineKeyboardButton("ToDo", callback_data=f"move:{task_id}:{Status.TODO.value}"),
        types.InlineKeyboardButton("InProgress", callback_data=f"move:{task_id}:{Status.IN_PROGRESS.value}"),
        types.InlineKeyboardButton("Done", callback_data=f"move:{task_id}:{Status.DONE.value}"),
    ]
    markup.add(*buttons)
    return markup


def _delete_keyboard(task_id: int) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Yes, delete", callback_data=f"delete_yes:{task_id}"),
        types.InlineKeyboardButton("Cancel", callback_data=f"delete_no:{task_id}"),
    )
    return markup


def _edit_keyboard(task_id: int) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Edit title", callback_data=f"edit_field:{task_id}:title"),
        types.InlineKeyboardButton("Edit description", callback_data=f"edit_field:{task_id}:description"),
    )
    return markup


def _format_task_line(task) -> str:
    title = html.escape(task.title)
    if task.description:
        return f"#{task.id} | {title} - {html.escape(task.description)}"
    return f"#{task.id} | {title}"


def _board_text(user_id: int) -> str:
    snapshot = task_service.board_snapshot(user_id)
    parts = ["<b>Kanban board</b>"]
    for status in (Status.TODO, Status.IN_PROGRESS, Status.DONE):
        parts.append(f"\n<b>{STATUS_TITLES[status]}</b>")
        tasks = snapshot[status]
        if not tasks:
            parts.append("  (empty)")
            continue
        for task in tasks:
            parts.append(f"  {_format_task_line(task)}")
    return "\n".join(parts)


def _board_move_keyboard(user_id: int) -> types.InlineKeyboardMarkup | None:
    tasks = task_service.list_tasks(user_id)
    if not tasks:
        return None
    markup = types.InlineKeyboardMarkup(row_width=2)
    for task in tasks:
        markup.add(types.InlineKeyboardButton(f"Move #{task.id}", callback_data=f"open_move:{task.id}"))
    return markup


@bot.message_handler(commands=["start", "help"])
def cmd_start(message):
    text = (
        "Commands:\n"
        "/new - create task\n"
        "/board - show board\n"
        "/list [todo|in_progress|done] - list tasks\n"
        "/edit &lt;id&gt; - edit title/description\n"
        "/move &lt;id&gt; - move to another column\n"
        "/delete &lt;id&gt; - delete task\n"
    )
    bot.reply_to(message, text)


@bot.message_handler(commands=["new"])
def cmd_new(message):
    sent = bot.reply_to(message, "Send task title:")
    bot.register_next_step_handler(sent, _new_receive_title, message.from_user.id)


def _new_receive_title(message, user_id: int):
    title = message.text or ""
    try:
        task_service._validate_title(title)
    except ValidationError as exc:
        sent = bot.reply_to(message, f"{exc}. Send title again:")
        bot.register_next_step_handler(sent, _new_receive_title, user_id)
        return
    sent = bot.reply_to(message, "Send description or '-' to skip:")
    bot.register_next_step_handler(sent, _new_receive_description, user_id, title)


def _new_receive_description(message, user_id: int, title: str):
    raw = (message.text or "").strip()
    description = None if raw == "-" else raw
    try:
        task = task_service.create_task(user_id, title=title, description=description)
    except ValidationError as exc:
        sent = bot.reply_to(message, f"{exc}. Send description again or '-' to skip:")
        bot.register_next_step_handler(sent, _new_receive_description, user_id, title)
        return
    bot.reply_to(message, f"Task created: #{task.id} ({STATUS_LABELS[task.status]})")


@bot.message_handler(commands=["board"])
def cmd_board(message):
    text = _board_text(message.from_user.id)
    keyboard = _board_move_keyboard(message.from_user.id)
    bot.reply_to(message, text, reply_markup=keyboard)


@bot.message_handler(commands=["list"])
def cmd_list(message):
    args = message.text.split(maxsplit=1)
    user_id = message.from_user.id
    try:
        if len(args) == 1:
            tasks = task_service.list_tasks(user_id)
        else:
            tasks = task_service.list_tasks(user_id, args[1].strip())
    except ValueError:
        bot.reply_to(message, "Use: /list [todo|in_progress|done]")
        return

    if not tasks:
        bot.reply_to(message, "No tasks found.")
        return

    lines = ["Tasks:"]
    for task in tasks:
        lines.append(f"{_format_task_line(task)} [{STATUS_LABELS[task.status]}]")
    bot.reply_to(message, "\n".join(lines))


@bot.message_handler(commands=["move"])
def cmd_move(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2 or not parts[1].isdigit():
        bot.reply_to(message, "Use: /move &lt;id&gt;")
        return
    task_id = int(parts[1])
    bot.reply_to(message, f"Choose new status for #{task_id}:", reply_markup=_status_keyboard(task_id))


@bot.callback_query_handler(func=lambda call: call.data.startswith("move:"))
def cb_move(call):
    _, task_id_raw, status_raw = call.data.split(":", maxsplit=2)
    user_id = call.from_user.id
    task_id = int(task_id_raw)
    try:
        task = task_service.move_task(user_id, task_id, status_raw)
    except TaskNotFoundError:
        bot.answer_callback_query(call.id, "Task not found")
        return
    except ValueError:
        bot.answer_callback_query(call.id, "Wrong status")
        return
    bot.answer_callback_query(call.id, "Moved")
    bot.send_message(call.message.chat.id, f"Task #{task.id} moved to {STATUS_LABELS[task.status]}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("open_move:"))
def cb_open_move(call):
    _, task_id_raw = call.data.split(":", maxsplit=1)
    task_id = int(task_id_raw)
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"Choose new status for #{task_id}:", reply_markup=_status_keyboard(task_id))


@bot.message_handler(commands=["delete"])
def cmd_delete(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2 or not parts[1].isdigit():
        bot.reply_to(message, "Use: /delete &lt;id&gt;")
        return
    task_id = int(parts[1])
    bot.reply_to(message, f"Delete task #{task_id}?", reply_markup=_delete_keyboard(task_id))


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def cb_delete(call):
    action, task_id_raw = call.data.split(":", maxsplit=1)
    task_id = int(task_id_raw)
    if action == "delete_no":
        bot.answer_callback_query(call.id, "Canceled")
        return
    try:
        task_service.delete_task(call.from_user.id, task_id)
    except TaskNotFoundError:
        bot.answer_callback_query(call.id, "Task not found")
        return
    bot.answer_callback_query(call.id, "Deleted")
    bot.send_message(call.message.chat.id, f"Task #{task_id} deleted")


@bot.message_handler(commands=["edit"])
def cmd_edit(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2 or not parts[1].isdigit():
        bot.reply_to(message, "Use: /edit &lt;id&gt;")
        return
    task_id = int(parts[1])
    bot.reply_to(message, f"What to edit in #{task_id}?", reply_markup=_edit_keyboard(task_id))


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_field:"))
def cb_edit_field(call):
    _, task_id_raw, field = call.data.split(":", maxsplit=2)
    task_id = int(task_id_raw)
    bot.answer_callback_query(call.id)
    if field == "title":
        sent = bot.send_message(call.message.chat.id, f"Send new title for #{task_id}:")
        bot.register_next_step_handler(sent, _edit_receive_title, call.from_user.id, task_id)
        return
    sent = bot.send_message(call.message.chat.id, f"Send new description for #{task_id} or '-' to clear:")
    bot.register_next_step_handler(sent, _edit_receive_description, call.from_user.id, task_id)


def _edit_receive_title(message, user_id: int, task_id: int):
    title = message.text or ""
    try:
        task = task_service.edit_task(user_id, task_id, title=title)
    except ValidationError as exc:
        sent = bot.reply_to(message, f"{exc}. Send title again:")
        bot.register_next_step_handler(sent, _edit_receive_title, user_id, task_id)
        return
    except TaskNotFoundError:
        bot.reply_to(message, "Task not found.")
        return
    bot.reply_to(message, f"Task #{task.id} title updated.")


def _edit_receive_description(message, user_id: int, task_id: int):
    raw = (message.text or "").strip()
    description = "" if raw == "-" else raw
    try:
        task = task_service.edit_task(user_id, task_id, description=description)
    except ValidationError as exc:
        sent = bot.reply_to(message, f"{exc}. Send description again or '-' to clear:")
        bot.register_next_step_handler(sent, _edit_receive_description, user_id, task_id)
        return
    except TaskNotFoundError:
        bot.reply_to(message, "Task not found.")
        return
    bot.reply_to(message, f"Task #{task.id} description updated.")


def run() -> None:
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    run()
