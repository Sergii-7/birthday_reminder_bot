from aiogram.types import CallbackQuery
from config import sb_telegram_id
from src.bot_app.create_bot import dp
from src.bot_app.menu import Menu, Settings
from src.sql import func_db
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)


@dp.callback_query(lambda callback_query: callback_query.data.startswith("0:"))
async def callback_run(callback_query: CallbackQuery):
    """ Get callback_query that startswith '0:' """
    data = callback_query.data[2:]
    message_id, telegram_id = callback_query.message.message_id, callback_query.from_user.id
    logger.info(f"callback_query.data: {callback_query.data}, telegram_id: {telegram_id}")
    menu = Menu()
    user = await func_db.get_user_by_telegram_id(telegram_id=telegram_id)
    if data in ["x", "m"]:
        ''' Delete sms with menu '''
        await callback_query.answer(text="ok")
        await callback_query.message.delete()
        if data == "m":
            ''' Give main_menu to user '''
            await menu.get_main_menu(user=user, pause=1)
    else:
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
                chats = await func_db.get_chats(user_id=user.id, limit=None)
                if chats:
                    if data == '1':
                        ''' 💳 номер вашої карти 💳 '''
                        await callback_query.message.delete()
                        card_number = chats[0].card_number
                        text_sms = (f"<b>Номер вашої банківської картки, яка вказана для отримання внесків:</b>\n\n"
                                    f"<code>{card_number}</code>\n\nps: Якщо ви хочете змінити номер картки, натисніть"
                                    f" <b>Tak ✔️</b> у вас з'явиться спеціальна форма, не змінюйте її, "
                                    f"лише додайте інший номер картки.")
                        text_to_insert = '\nnew card number:\n'
                        setting = Settings(telegram_id=telegram_id, text_sms=text_sms, text_to_insert=text_to_insert)
                        await setting.admin_commands(photo="bank_card.jpg")
                    elif data == '2':
                        ''' Керувати учасниками чатів '''
                        ...
                    elif data == '3':
                        ''' 🎆 Створити подію 🎇 '''
                        ...
                    elif data == '4':
                        ''' 💰 Звіт по внескам 💰 '''
                        ...
                    elif data == '5':
                        ''' ☢️ Передати права адміна ☣️ '''
                        ...
                else:
                    ''' user не має чатів і не може бути адміном '''
                    text = "Ви не маєте повноважень приймати внески з будь-якого чату 🤷"
                    await callback_query.answer(text=text, show_alert=True)
                    if telegram_id != sb_telegram_id:
                        user.info = None
                        user = await func_db.doc_update(doc=user)
                        await callback_query.message.delete()
                        await menu.get_main_menu(user=user)
            else:
                await callback_query.answer(text="У вас немає доступу!", show_alert=True)
                await callback_query.message.delete()
        elif data.startswith("super"):
            ''' callback from super '''
            if user.status == "super-admin" or telegram_id == sb_telegram_id:
                type_menu = data.replace("super", "")  # 0 | 1 |
                await menu.for_super_admin(user=user, message_id=message_id, type_menu=type_menu)
            else:
                await callback_query.answer(text="У вас немає доступу!", show_alert=True)
                await callback_query.message.delete()


# import asyncio
# text_sms = (f"<b>Номер вашої банківської картки, яка вказана для отримання внесків:</b>\n\n"
#             f"<code>1234567898765412</code>\n\nps: Якщо ви хочете змінити номер картки, натисніть"
#             f" <b>Tak ✔️</b> у вас з'явиться спеціальна форма, не змінюйте її, "
#             f"лише додайте інший номер картки.")
# text_to_insert = '\nnew card number:\n'
# setting = Settings(telegram_id=sb_telegram_id, text_sms=text_sms, text_to_insert=text_to_insert)
# asyncio.run(setting.admin_commands(photo="bank_card.jpg"))