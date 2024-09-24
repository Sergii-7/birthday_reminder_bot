import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

""" Визначаємо шлях до файлів з логами відносно кореневої директорії проекту """
# Отримуємо абсолютний шлях до кореневої директорії проекту
project_root = os.path.dirname(os.path.abspath(__file__))
file_log_tel_bot = os.path.join(project_root, 'logs', 'tel_bot.log')
file_log_fast_api = os.path.join(project_root, 'logs', 'fast_api.log')

""" DataBase 'birthday_bot' on Linux Ubuntu in Digital Ocean """
URI_DB = os.environ.get('UBUNTU_URI_DB')

""" Telegram Bot """
TOKEN = os.environ.get('TOKEN')
bot_name = "Holiday organizer"
bot_link = "https://t.me/holiday_organizer_bot"
sb_telegram_id = 620527199
WEBHOOK_PATH = '/telegram/api/bot/hr/set/webhook/path/a/b/c/d/e'
HOST = 'https://hr-api-hj3x6.ondigitalocean.app'
WEBHOOK_URL = f'{HOST}{WEBHOOK_PATH}'