from pathlib import Path
import os

import telebot
from telebot import types

from kanban.storage import JsonStorage
from kanban.task_service import TaskServiсe
from telebot import apihelper

from dotenv import load_dotenv

load_dotenv()


apihelper.proxy = {"https": "socks5://10.0.2.2:12335"}
token = os.getenv("BOT_TOKEN")


store = JsonStorage(Path("data") / "kanban.json")
task_service = TaskServiсe(store)

bot = telebot.TeleBot(token, parse_mode="HTML")


@bot.message_handler(commands=["start"])
def hello(message):
    bot.send_message(message.chat.id, "Приветики, я бот для расписаний.")


@bot.message_handler(commands=["new_task"])
def add_new_task(message):
    # "/new_task Название задачи - Описание задачи"
    text = message.text.lstrip("/new_task").strip()
    if not text:
        bot.send_message(
            message.chat.id,
            (
                "Для того, чтобы создать задачу укажи:\n"
                "/new_task Название задачи - Описание задачи"
            ),
        )
    else:
        name, description = text.split(" - ")
        task = task_service.create_task(message.chat.id, name, description)
        bot.send_message(
            message.chat.id,
            ("Задача создана успешно и занесена в список задач.\n"
             "Название новой задачи: \n" 
             f"{task.name}"),
        )

@bot.message_handler(commands=["get_tasks"])
def get_all_tasks(message):
    tasks = task_service.get_tasks(message.chat.id)
    markup = types.InlineKeyboardMarkup(row_width=3)
    for task in tasks:
        markup.add(types.InlineKeyboardButton(task.name, callback_data="task_{task.id}"))
    bot.send_message(
        message.chat.id,
        "Задачи:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("task_"))
def get_task_info(call):
    task_id = int(call.data.lstrip("task_"))
    user_id = int(call.message.chat.id)
    one_task = store.get_task_by_id(user_id, task_id)
    # markup = types.InlineKeyboardMarkup(row_width=3)
    # TODO: добавить клавиатуру с изменением задачи
    bot.send_message(
        call.message.chat.id,
        (f"Имя задачи: {one_task.name}\n"
         f"Описание зада: {one_task.description}\n"
         f"Статус задачи: {one_task.status.value}"),
    )


def run() -> None:
    bot.infinity_polling(skip_pending=True)
