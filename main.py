import logging
import sqlite3
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ChatType
from aiogram.utils import executor
from aiogram import types

from dotenv import load_dotenv
import os
import yaml

# Загрузка переменных окружения из файла .env
load_dotenv()

# Установка уровня логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
API_TOKEN = os.getenv('API_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Инициализация базы данных SQLite3
db_name = os.getenv('DB_NAME', 'join_requests.db')
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Загрузка конфигурации из файла YAML
config_file = 'config.yaml'
with open(config_file, 'r') as stream:
    config = yaml.safe_load(stream)

# Обработчик события присоединения пользователя к чату
@dp.chat_join_request_handler()
async def join_request(update: types.ChatJoinRequest):
    user_id = update.from_user.id
    username = update.from_user.username
    chat_id = update.chat.id
    timestamp = update.date
    request_ad = config['messages']['request_ad']
    ad_message = config['messages']['join_request_ad']
    if request_ad:
        # Отправка рекламного сообщения
        await bot.send_message(user_id, ad_message)

    # Добавление пользователя в базу данных
    cursor.execute('''
        INSERT OR REPLACE INTO join_requests (user_id, username, chat_id, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, chat_id, timestamp))
    conn.commit()

    # Одобрение присоединения пользователя к чату
    await update.approve()

# Запуск бота
if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
