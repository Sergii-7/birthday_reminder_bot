from aiogram.types import Update
from fastapi import Request, status

from config import WEBHOOK_PATH
from src.bot_app.create_bot import bot, dp
from src.service.loggers.py_logger_tel_bot import get_logger
from src.web_app.create_app import app

logger = get_logger(__name__)


@app.post(path=WEBHOOK_PATH, include_in_schema=False, status_code=status.HTTP_200_OK)
async def handle_webhook(request: Request):
    """Route for web hook from Telegram Server."""
    try:
        update = await request.json()
        logger.debug(f"Received update: {update}")
        telegram_update = Update(**update)
        await dp.feed_update(bot=bot, update=telegram_update)
    except Exception as e:
        logger.error(e)
    return {"status": "ok"}
