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


def run() -> None:
    bot.infinity_polling(skip_pending=True)
