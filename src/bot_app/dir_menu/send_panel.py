from aiogram.types import InlineKeyboardMarkup

from src.bot_app.create_bot import bot
from src.bot_app.dir_menu.buttons_for_menu import buttons_for_event_settings
from src.dir_schedule.some_tools import DataAI
from src.sql.func_db import get_doc_by_id
from src.sql.models import User, Chat, Holiday


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