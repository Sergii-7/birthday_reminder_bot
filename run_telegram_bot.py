from asyncio import run as asyncio_run
from src.bot_app.create_bot import bot
from config import WEBHOOK_URL
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)


async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)  # Set webhook при запуску додатку
    logger.info("Bot webhook has been set.")


if __name__ == "__main__":
    asyncio_run(main=on_startup())