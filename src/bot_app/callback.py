from aiogram.types import CallbackQuery, FSInputFile
from src.bot_app.create_bot import bot, dp
from src.bot_app.menu import Menu
from src.sql import func_db
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)

menu = Menu()


@dp.callback_query(lambda callback_query: callback_query.data.startswith("0:"))
async def callback_run(callback_query: CallbackQuery):
    """ Get callback_query that startswith '0:' """
    data = callback_query.data[2:]
    message_id, telegram_id = callback_query.message.message_id, callback_query.from_user.id
    logger.info(f"callback_query.data: {callback_query.data}, telegram_id: {telegram_id}")
    if data == "x":
        ''' Del sms with buttons '''
        await callback_query.answer(url='avrora.ua')
        await callback_query.message.delete()
    elif data.startswith("user"):
        ''' callback from user '''
        data = data.replace("user", "")
        if data == '1':
            ''' Change Birthday '''
            await callback_query.message.delete()
            await menu.request_birthday(user=await func_db.get_user_by_telegram_id(telegram_id=telegram_id))

    elif data.startswith("admin"):
        ''' callback from admin '''
        data = data.replace("admin", "")
        ...
    elif data.startswith("super"):
        ''' callback from super '''
        data = data.replace("super", "")
        ...


