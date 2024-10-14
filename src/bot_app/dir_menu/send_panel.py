from asyncio import sleep
from aiogram.types import InlineKeyboardMarkup, CallbackQuery
from typing import List, Optional

from src.bot_app.create_bot import bot
from src.bot_app.dir_menu.buttons_for_menu import buttons_for_event_settings
from src.dir_schedule.some_tools import DataAI
from src.sql.func_db import get_doc_by_id, get_chats, get_report, get_holiday
from src.sql.models import User, Chat, Holiday, Report


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
            holiday: Holiday = await get_holiday(user_pk=user.id, chat_pk=chat.id)
            report: Optional[Report] = await get_report(user_pk=user.id, chat_pk=chat.id, holiday_pk=holiday.id)
            if report:
                if not report.status:
                    """User has financial debt before this chat"""
                    title = await DataAI().get_title(chat=chat)
                    if n < 6:
                        text += (f"\n\nчат: <b>{title}</b>\n"
                                 f"<u>Іменинник/іменинниця:</u>\n{holiday.info}\n"
                                 f"Дата Народження: <code>{holiday.date_event}</code>\n"
                                 f"сума внеску: <b>{holiday.amount}</b>\n"
                                 f"\n\nкарта для перерахування внеску: <code>{chat.card_number}</code>")
                    else:
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