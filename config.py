import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

""" Отримуємо абсолютний шлях до кореневої директорії проекту """
project_root = os.path.dirname(os.path.abspath(__file__))

""" Визначаємо шлях до файлів з логами відносно кореневої директорії проекту """
file_log_tel_bot = os.path.join(project_root, 'logs', 'tel_bot.log')
file_log_fast_api = os.path.join(project_root, 'logs', 'fast_api.log')

""" Path to directory with media files """
media_file_path = os.path.join(project_root, 'src/media/')

""" DataBase 'birthday_bot' on Linux Ubuntu in Digital Ocean """
URI_DB = os.environ.get('UBUNTU_URI_DB')

""" Telegram Bot """
TOKEN = os.environ.get('TOKEN')
bot_name = "Holiday organizer"
bot_link = "https://t.me/holiday_organizer_bot"
bot_user_name = "@holiday_organizer_bot"
sb_telegram_id = 620527199
HOST = 'https://holiday-organizer-dp6b4.ondigitalocean.app'
WEBHOOK_PATH = '/telegram/api/bot/hr/set/webhook/path/a/b/c/d/e'
WEBHOOK_URL = f'{HOST}{WEBHOOK_PATH}'