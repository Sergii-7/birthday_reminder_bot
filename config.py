import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

""" Визначаємо шлях до файлів з логами відносно кореневої директорії проекту """
# Отримуємо абсолютний шлях до кореневої директорії проекту
project_root = os.path.dirname(os.path.abspath(__file__))
file_log_tel_bot = os.path.join(project_root, 'logs', 'tel_bot.log')
file_log_fast_api = os.path.join(project_root, 'logs', 'fast_api.log')


URI_DB = ''