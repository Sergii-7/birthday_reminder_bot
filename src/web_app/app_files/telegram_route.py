from fastapi import Request, status
from aiogram.types import Update
from create_app import app
from src.bot_app.create_bot import bot, dp
from config import WEBHOOK_PATH #, WEBHOOK_URL
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)


# @app.on_event("startup")
# async def on_startup():
#     await bot.delete_webhook(drop_pending_updates=True)
#     await bot.set_webhook(WEBHOOK_URL)  # Set webhook при запуску додатку
#     logger.info("Bot webhook has been set.")


@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook(drop_pending_updates=True)  # Delete webhook при зупинці
    await bot.session.close()
    logger.info("Bot webhook has been delete.")


@app.post(path=WEBHOOK_PATH, include_in_schema=False, status_code=status.HTTP_200_OK)
async def handle_webhook(request: Request):
    update = await request.json()
    logger.info(f"Received update: {update}")
    telegram_update = Update(**update)
    await dp.feed_update(bot=bot, update=telegram_update)  # Передаємо bot та update
    return {"status": "ok"}