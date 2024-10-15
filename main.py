import uvicorn
""" імпортуємо об'єкт 'app' """
from create_app import app
""" імпортуємо всі файли з маршрутами """
from src.web_app.app_files import admin_route, user_route, telegram_route
""" імпортуємо всі файли з хендлерами від aiogram """
from src.bot_app import command, message, callback

# запуск локального серверу: uvicorn main:app --reload
# подивитися інтер-активну документацію: {host}/docs
# подивитися повну документацію: {host}/redoc


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        workers=2
    )