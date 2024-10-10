from aiogram.types import InlineKeyboardButton, KeyboardButton
from typing import List, Dict
from config import HOST

""" Buttons for menu """

b_contact = [KeyboardButton(text='поділитися контактом', request_contact=True)]
b_remove_panel = [InlineKeyboardButton(text="🫣 сховати панель 🫣", callback_data="0:x")]
b_add_group = [InlineKeyboardButton(text="👫👫 Додати групу 👫👫", callback_data="0:super_set_chat_0")]


def buttons_for_user() -> List[List[InlineKeyboardButton]]:
    b1 = [InlineKeyboardButton(text="🎂 Змінити дату ДР 🎂", callback_data=f"0:user1")]
    b2 = [InlineKeyboardButton(text="📅 Календар подій 📅", callback_data=f"0:user2")]
    b3 = [InlineKeyboardButton(text="💵 Зробити внесок 💵", callback_data=f"0:user3")]
    buttons = [b for b in [b1, b2, b3]]
    return buttons


def b_web_app_birthday(telegram_id: int, password: str) -> List[InlineKeyboardButton]:
    """"""
    web_app: Dict[str, str] = {'url': f"{HOST}/path/login/{telegram_id}/{password}"}
    return [InlineKeyboardButton(text="🎂 🥳 🎉", web_app=web_app)]


def b_my_groups(role: str) -> List[InlineKeyboardButton]:
    """ Create button '⚙️ Мої групи ⚙️' for admin or super-admin """
    role = "super" if role == "super-admin" else "admin"
    return [InlineKeyboardButton(text="⚙️ Мої групи ⚙️", callback_data=f"0:{role}:m")]


def buttons_for_chat_settings(role: str, chat_doc_id: int) -> List[List[InlineKeyboardButton]]:
    buttons = list()
    buttons.append([InlineKeyboardButton(
        text="💳 Номер вашої карти 💳", callback_data=f"0:{role}:set:card:{chat_doc_id}")])
    buttons.append([InlineKeyboardButton(
        text="🧔🏼 Користувачі чатів 👨‍🦱", callback_data=f"0:{role}:set:users:{chat_doc_id}")])
    buttons.append([InlineKeyboardButton(
        text="🎆 Створити подію 🎇", callback_data=f"0:{role}:set:holiday:{chat_doc_id}")])
    buttons.append([InlineKeyboardButton(
        text="💰 Звіт по внескам 💰", callback_data=f"0:{role}:set:report:{chat_doc_id}")])
    buttons.append([InlineKeyboardButton(
        text="☢️ Передати права адміна ☣️", callback_data=f"0:{role}:set:change_admin:{chat_doc_id}")])
    buttons.append(b_remove_panel)
    return buttons


def b_chat_settings(role: str, chat_doc_id: int) -> List[InlineKeyboardButton]:
    return [InlineKeyboardButton(text="⚙️ налаштування ⚙️", callback_data=f"0:{role}_set_chat_{chat_doc_id}")]


def buttons_for_admin_command(text_to_insert: str) -> List[InlineKeyboardButton]:
    """ buttons for 'class Settings().admin_commands()' """
    b_yes = InlineKeyboardButton(text="Tak ✔️", switch_inline_query_current_chat=text_to_insert)
    b_not = InlineKeyboardButton(text="Hi 🙅", callback_data="0:m")
    return [b_yes, b_not]

