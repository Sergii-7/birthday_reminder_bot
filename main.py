import uvicorn

from src.bot_app import callback, command, message
from src.web_app.app_files import admin_route, check_route, telegram_route, user_route
from src.web_app.create_app import app

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, workers=1)
