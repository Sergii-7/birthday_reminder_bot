from asyncio import sleep
from aiogram.types import InlineKeyboardMarkup, CallbackQuery
from typing import List, Optional

from config import bot_link
from src.bot_app.create_bot import bot
from src.bot_app.dir_menu.buttons_for_menu import buttons_for_event_settings
from src.dir_schedule.some_tools import DataAI
from src.sql.func_db import get_doc_by_id, get_chats, get_report, get_holiday
from src.sql.models import User, Chat, Holiday, Report, UserChat


async def panel_set_holidays(chat: Chat, holiday: Holiday):
    """Send panel for Admin to set Holiday in DataBase"""
    title = await DataAI().get_title(chat=chat)
    admin: User = await get_doc_by_id(model='user', doc_id=chat.user_id)
    text = (f"чат: <b>{title}</b>\n"
            f"<u>Іменинник/іменинниця:</u>\n{holiday.info}\n"
            f"Дата Народження: <code>{holiday.date_event}</code>\n"
            f"сума внеску: <b>{holiday.amount}</b>")
    buttons = buttons_for_event_settings(role=admin.info, holiday=holiday)
    reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(
        chat_id=admin.telegram_id, text=text, reply_markup=reply_markup)


async def panel_make_payment(user: User, callback_query: CallbackQuery):
    """User check debt before his chats"""
    chats: List[Chat] = await get_chats(user_id=user.id)
    if chats:
        text, text_list = str(), list()
        for n, chat in enumerate(start=1, iterable=chats):
            holiday: Optional[Holiday] = await get_holiday(user_pk=user.id, chat_pk=chat.id)
            if holiday:
                report: Optional[Report] = await get_report(user_pk=user.id, chat_pk=chat.id, holiday_pk=holiday.id)
                if report:
                    if not report.status:
                        """User has financial debt before this chat"""
                        title = await DataAI().get_title(chat=chat)
                        text += (f"\n\nчат: <b>{title}</b>\n"
                                 f"<u>Іменинник/іменинниця:</u>\n{holiday.info}\n"
                                 f"Дата Народження: <code>{holiday.date_event}</code>\n"
                                 f"сума внеску: <b>{holiday.amount}</b>\n"
                                 f"карта для перерахування внеску: <code>{chat.card_number}</code>")
                        if n % 5 == 0:
                            text_list.append(text)
                            text = ""
        if text:
            text_list.append(text)
        if text_list:
            for sms in text_list:
                await bot.send_message(chat_id=user.telegram_id, text=sms)
                await sleep(delay=1)
            return
        else:
            text = "На даний момент у вас немає боргів перед групами."
            await callback_query.answer(text=text, show_alert=True)
    else:
        text = "Ви не належите до жодного чату, до якого можете робити внесок."
        await callback_query.answer(text=text, show_alert=True)
    await callback_query.message.delete()


async def text_payment_info_with_set_link(report: Report, user_chat: UserChat, user: User = None) -> str:
    """Info text for Admin about User payment history with link - change report.status"""
    user: User = user_chat.user if not user else user
    username = f"@{user.username}\n" if user.username else ""
    phone_number = f"телефон <code>{user.phone_number}</code>\n" if user.phone_number else ""
    birthday = str(user.birthday)[5:] if user.birthday else 'дані не внесені'
    birthday = f"день народження (month-day): <code>{birthday}</code>"
    desc = "<b>🎉 вже робив внесок 🥳</b>" if report.status else "<b>🤬 ще не зробив внесок 😡</b>"
    link_settings = f"\n{desc} <a href='{bot_link}?start=set-report-{report.id}'>змінити</a>"
    text = f"<b>{user.first_name}</b>\n{username}{phone_number}{birthday}{link_settings}"
    return text