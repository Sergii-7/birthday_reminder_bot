from aiogram.types import CallbackQuery, FSInputFile
from src.bot_app.create_bot import bot, dp
from src.bot_app.menu import Menu
from src.sql import func_db
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)


@dp.callback_query(lambda callback_query: callback_query.data.startswith("0:"))
async def callback_run(callback_query: CallbackQuery):
    """ Get callback_query that startswith '0:' """
    data = callback_query.data[2:]
    message_id, telegram_id = callback_query.message.message_id, callback_query.from_user.id
    logger.info(f"callback_query.data: {callback_query.data}, telegram_id: {telegram_id}")
    if data == "x":
        ''' Delete sms with menu '''
        await callback_query.answer(text="ok")
        await callback_query.message.delete()
    else:
        menu = Menu()
        user = await func_db.get_user_by_telegram_id(telegram_id=telegram_id)
        if data.startswith("user"):
            ''' callback from user '''
            data = data.replace("user", "")
            if data == '1':
                ''' Change Birthday '''
                await callback_query.message.delete()
                await menu.request_birthday(user=user)
            elif data == '2':
                ''' Calendar with holidays '''
                ...
            elif data == '3':
                ''' Make payment '''
                ...
        elif data.startswith("admin"):
            ''' callback from admin '''
            if user.info in ['admin', 'super-admin']:
                data = data.replace("admin", "")
                if data == '1':
                    '''  '''
                    ...
                elif data == '2':
                    '''  '''
                    ...
            else:
                await callback_query.answer(text="У вас немає доступу!", show_alert=True)
                await callback_query.message.delete()
        elif data.startswith("super"):
            ''' callback from super '''
            if user.status == "super-admin":
                data = data.replace("super", "")
                if data == '1':
                    ''' ⚙️ керувати групами ⚙️ '''
                    ...
                elif data == '2':
                    '''  '''
                    ...
            else:
                await callback_query.answer(text="У вас немає доступу!", show_alert=True)
                await callback_query.message.delete()
