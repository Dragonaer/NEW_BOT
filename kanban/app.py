from pathlib import Path
import os

import telebot
from telebot import types

from kanban.storage import JsonStorage
from kanban.task_service import TaskServiсe

from dotenv import load_dotenv
load_dotenv()


token = os.getenv('BOT_TOKEN')


store = JsonStorage(Path("data") / "kanban.json")
task_service = TaskServiсe(store)

bot = telebot.TeleBot(token, parse_mode="HTML")

@bot.message_handler(commands=["start"])
def hello(message):
    bot.send_message(
        message.chat.id,
        "Привет, я бот для расписаний"
    )

def run() -> None:
    bot.infinity_polling(skip_pending=True)