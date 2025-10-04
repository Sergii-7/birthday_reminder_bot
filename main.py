import uvicorn

from create_app import app
from src.bot_app import callback, command, message
from src.web_app.app_files import admin_route, telegram_route, user_route

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, workers=1)
