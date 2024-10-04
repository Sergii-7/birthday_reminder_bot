from aiogram.types import CallbackQuery, FSInputFile
from src.bot_app.create_bot import bot, dp
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)


@dp.callback_query(lambda callback_query: callback_query.data.startswith("0:"))
async def callback_run(callback_query: CallbackQuery):
    """ Get callback_query that startswith '0:' """
    data = callback_query.data[2:]
    message_id, telegram_id = callback_query.message.message_id, callback_query.from_user.id
    logger.info(f"callback_query.data: {callback_query.data}, telegram_id: {telegram_id}")
    if data == "some_data":
        pass

