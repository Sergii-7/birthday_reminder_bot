from aiogram.types import InlineKeyboardButton, KeyboardButton
from typing import List, Dict
from config import HOST

""" Buttons for menu """
b1 = [InlineKeyboardButton(text="🎂 Змінити дату ДР 🎂", callback_data=f"0:user1")]
b2 = [InlineKeyboardButton(text="📅 Календар подій 📅", callback_data=f"0:user2")]
b3 = [InlineKeyboardButton(text="💵 Зробити внесок 💵", callback_data=f"0:user3")]
b_contact = [KeyboardButton(text='поділитися контактом', request_contact=True)]
b_remove_panel = [InlineKeyboardButton(text="🫣 сховати панель 🫣", callback_data="0:x")]
b_add_group = [InlineKeyboardButton(text="👫👫 Додати групу 👫👫", callback_data="0:super_set_chat_0")]


def b_web_app_birthday(telegram_id: int, password: str) -> List[InlineKeyboardButton]:
    """"""
    web_app: Dict[str, str] = {'url': f"{HOST}/path/login/{telegram_id}/{password}"}
    return [InlineKeyboardButton(text="🎂 🥳 🎉", web_app=web_app)]


def b_my_groups(role: str) -> List[InlineKeyboardButton]:
    """ Create button '⚙️ Мої групи ⚙️' for admin or super-admin """
    role = "super" if role == "super-admin" else "admin"
    return [InlineKeyboardButton(text="⚙️ Мої групи ⚙️", callback_data=f"0:{role}:m")]


