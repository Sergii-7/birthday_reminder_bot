import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

"""Сума внеску (грн)"""
amount = 500

""" Отримуємо абсолютний шлях до кореневої директорії проекту """
project_root = os.path.dirname(os.path.abspath(__file__))

""" Визначаємо шляхи до статичних файлів та шаблонів відносно кореневої директорії проекту """
STATIC_FILES = os.path.join(project_root, "src", "web_app", "static")
TEMPLATES = os.path.join(project_root, "src", "web_app", "templates")

""" Визначаємо шлях до файлів з логами відносно кореневої директорії проекту """
file_log_tel_bot = os.path.join(project_root, "logs", "tel_bot.log")
file_log_fast_api = os.path.join(project_root, "logs", "fast_api.log")
file_log_openai = os.path.join(project_root, "logs", "openai.log")
file_log_sql = os.path.join(project_root, "logs", "sql.log")

""" Path to directory with media files """
media_file_path = os.path.join(project_root, "src/media/")

"""Redis Settings"""
REDIS_PORT = 6379
REDIS_HOST = "localhost"
REDIS_TIMEOUT = 10
REDIS_NUMBER_DB = 2
# REDIS_MAX_CONNECTIONS = 10

""" DataBase 'birthday_bot' on Linux Ubuntu in Digital Ocean """
URI_DB = os.environ.get("UBUNTU_URI_DB")

"""Connect to DataBase 'BirthdayBot' on MongoDB."""
MONGO_URI = os.environ.get("MONGO_URI")

""" API_KEY_OPENAI # для підключення model="gpt-4.0" """
API_KEY_OPENAI = os.environ.get("API_KEY_OPENAI")

""" Telegram Bot """
TOKEN = os.environ.get("TOKEN")
bot_name = "Holiday organizer"
bot_link = os.environ.get("BOT_LINK")
bot_user_name = os.environ.get("BOT_USER_NAME")
sb_telegram_id = int(os.environ.get("SB_TELEGRAM_ID"))
HOST = os.environ.get("HOST")
WEBHOOK_PATH = os.environ.get("WEBHOOK_PATH")
WEBHOOK_URL = f"{HOST}{WEBHOOK_PATH}"
my_admin_chat = int(os.environ.get("MY_ADMIN_CHAT"))
get_chat_id_bot = "@GetChatID_IL_BOT"

my_banc_card = os.environ.get("MY_BANC_CARD")

""" Valid groups for bot."""
GROUP_R_D = int(os.environ.get("GROUP_R_D", 0))
GROUP_TEST = int(os.environ.get("GROUP_TEST", 0))
VALID_GROUPS_FOR_BOT = [GROUP_R_D, GROUP_TEST]
