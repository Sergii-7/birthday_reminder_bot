from asyncio import sleep as asyncio_sleep
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from config import sb_telegram_id
from src.bot_app.create_bot import dp
from src.bot_app.dir_menu.buttons_for_menu import b_menu
from src.bot_app.dir_menu.menu import Menu, AdminMenu, SetChat, SetEvent
from src.bot_app.dir_menu.send_panel import panel_make_payment
from src.bot_app.dir_service.calendar_m import get_schedule_holidays
from src.sql import func_db
from src.sql.models import User, Chat, Report, Holiday
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)


@dp.callback_query(lambda callback_query: callback_query.data.startswith("0:"))
async def callback_run(callback_query: CallbackQuery):
    """ Get callback_query that startswith '0:' """
    data = callback_query.data[2:]
    message_id, telegram_id = callback_query.message.message_id, callback_query.from_user.id
    logger.info(f"callback_query.data: {callback_query.data}, telegram_id: {telegram_id}")
    menu = Menu()
    user: User = await func_db.get_user_by_telegram_id(telegram_id=telegram_id)
    if data in ["x", "m", "b"]:
        await callback_query.answer(text="ok")
        ''' Delete sms with menu '''
        if data in ["x", "m"]:
            await callback_query.message.delete()
        if data in ["m", "b"]:
            ''' Give main_menu to user '''
            await menu.get_main_menu(user=user, pause=0.5)
    else:
        if data.startswith("user"):
            ''' callback from user '''
            data = data.replace("user", "")
            if data == '1':
                ''' "🎂 Змінити дату ДР 🎂" '''
                await callback_query.message.delete()
                await menu.request_birthday(user=user)
            elif data == '2':
                ''' "📅 Календар подій 📅" '''
                text_list = await get_schedule_holidays(user=user)
                for text in text_list:
                    reply_markup = InlineKeyboardMarkup(inline_keyboard=[b_menu]) if text == text_list[-1] else None
                    text = f"<b>📅 Календар подій 📅</b>\n ------------\n{text}" if text == text_list[0] else text
                    await callback_query.message.answer(text=text, reply_markup=reply_markup)
                    await asyncio_sleep(1)
                await callback_query.message.delete()
            elif data == '3':
                ''' "💵 Зробити внесок 💵" '''
                await panel_make_payment(user=user, callback_query=callback_query)

        elif data.startswith("admin") or data.startswith("super"):
            ''' callback from admin or super-admin '''
            if user.info in ["super-admin", "admin"] or telegram_id == sb_telegram_id:
                admin_menu = AdminMenu()
                role = "super" if user.status == "super-admin" or telegram_id == sb_telegram_id else "admin"
                data = data[5:]
                if data == ":m" or "_set_chat_" in data:
                    type_menu = data
                    await admin_menu.get_chats_list(user=user, message_id=message_id, type_menu=type_menu, role=role)
                elif ":set:" in data:
                    """ Налаштування чату """
                    data = data.replace(":set:", "").split(":")
                    command, chat_pk = data[0], int(data[-1])
                    chat: Chat = await func_db.get_chat_with_user(pk=chat_pk)
                    if chat and chat.status:
                        await SetChat().get_command(user=user, chat=chat, command=command)
                    else:
                        text = "🤬 Ви або Телеграм-бот не мають доступу до цієї групи!"
                        await callback_query.answer(text=text, show_alert=True)
                        await callback_query.message.delete()
                elif ":event_" in data:
                    """ Event settings """
                    data = data.replace(":event_", "", 1).split(":")
                    command, holiday_id = data[0], int(data[-1])
                    holiday: Holiday = await func_db.get_holiday_with_chat(holiday_id=holiday_id)
                    await SetEvent().get_command(
                        user=user, command=command, holiday=holiday, callback_query=callback_query)
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