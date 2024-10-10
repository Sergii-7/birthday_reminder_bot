from aiogram.types import CallbackQuery
from config import sb_telegram_id, bot_link
from src.bot_app.create_bot import dp
from src.bot_app.dir_menu.menu import Menu, AdminMenu, SetChat
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
            await menu.get_main_menu(user=user, pause=0.5)
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
        elif data.startswith("admin") or data.startswith("super"):
            ''' callback from admin or super-admin '''
            if user.status in ["super-admin", "admin"] or telegram_id == sb_telegram_id:
                admin_menu = AdminMenu()
                role = "super" if user.status == "super-admin" or telegram_id == sb_telegram_id else "admin"
                data = data.replace("admin", "").replace("super", "")
                if data == ":m" or "_set_chat_" in data:
                    type_menu = data
                    await admin_menu.get_chats_list(user=user, message_id=message_id, type_menu=type_menu, role=role)
                elif ":set:" in data:
                    """ Налаштуваня чату """
                    data = data.replace(":set:", "").split(":")
                    command, chat_pk = data[0], int(data[-1])
                    chat = await func_db.get_chat_with_user(pk=chat_pk)
                    if chat and chat.status:
                        await callback_query.answer(text=command)
                        await SetChat().get_command(user=user, chat=chat, command=command)
                    else:
                        text = "🤬 Ви або Телеграм-бот не мають доступу до цієї групи!"
                        await callback_query.answer(text=text, show_alert=True)
                        await callback_query.message.delete()
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