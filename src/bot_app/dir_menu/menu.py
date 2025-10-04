import os
from asyncio import sleep as asyncio_sleep
from time import pthread_getcpuclockid
from typing import Any, List, Optional, Union

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, ReplyKeyboardMarkup

from config import get_chat_id_bot, media_file_path, sb_telegram_id
from src.bot_app.create_bot import bot
from src.bot_app.dir_menu.buttons_for_menu import *
from src.bot_app.dir_menu.send_panel import panel_set_holidays, text_payment_info_with_set_link
from src.bot_app.dir_service.bot_service import get_chat_info, get_user_info
from src.dir_schedule.some_tools import DataAI
from src.service.create_data import user_data
from src.service.loggers.py_logger_tel_bot import get_logger
from src.sql import func_db
from src.sql.models import Chat, Report, User, UserChat

logger = get_logger(__name__)


class Menu:
    """Menu buttons"""

    async def start_command(self, user: User, message_text: str = None):
        """Перевіряємо користувача та або даємо йому головне меню або запитуємо у нього додаткові дані"""
        if user.phone_number:
            if user.birthday:
                """Даємо користувачу головне меню"""
                await self.get_main_menu(user=user, message_text=message_text)
            else:
                """Робимо запит на отримання даних про день народження: sms + miniapp"""
                await self.request_birthday(user=user)
        else:
            """Робимо запит на отримання номеру телефону користувача"""
            await self.request_phone_number(user=user)

    async def request_phone_number(self, user: User):
        """Робимо запит на номер телефону"""
        text = "Поділиться своїм номером телефону за допомогою кнопкою нижче 👇"
        reply_markup = ReplyKeyboardMarkup(keyboard=[b_contact], resize_keyboard=True, one_time_keyboard=True)
        await bot.send_message(chat_id=user.telegram_id, text=text, reply_markup=reply_markup)

    async def request_birthday(self, user: User):
        """Робимо запит на отримання даних про день народження: sms + miniapp"""
        user_login = await func_db.get_login_user_by_telegram_id(telegram_id=user.telegram_id)
        b_web_app = b_web_app_birthday(telegram_id=user.telegram_id, password=user_login.password)
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                b_web_app,
            ]
        )
        text = "Вказати свій День Народження"
        await bot.send_message(chat_id=user.telegram_id, text=text, reply_markup=reply_markup)

    async def get_main_menu(self, user: User, message_text: str = None, pause: Union[int, float] = None):
        """Даємо користувачу головне меню"""
        """ menu for everybody (data users) """
        buttons = buttons_for_user()
        if user.info in ["admin", "super-admin"]:
            buttons.append(b_my_groups(role=user.info))
            if user.info == "super-admin" or user.telegram_id == sb_telegram_id:
                buttons.append(b_add_group)
        buttons.append(b_remove_panel)
        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        photo = FSInputFile(path=f"{media_file_path}admin_panel.jpg")
        text: str = f"Привіт, {user.first_name}!"
        if pause and isinstance(pause, (int, float)):
            await asyncio_sleep(delay=pause)
        await bot.send_photo(chat_id=user.telegram_id, caption=text, photo=photo, reply_markup=reply_markup)


class AdminMenu:
    """Get menu for admin or super-admin"""

    async def add_new_chat(self, user: User):
        """Add new chat"""
        text_sms: str = (
            f"Якщо ви бажаєте створити нову групу, натисніть <b>Tak ✔️</b> у вас з'явиться "
            f"спеціальна форма, не змінюйте її, лише додайте chat_id цієї групи.\n"
            f"ps: Дізнатися chat_id можна за допомогою цього бота: {get_chat_id_bot}"
        )
        text_to_insert = "\nnew chat_id:\n"
        setting = Settings(telegram_id=user.telegram_id, text_sms=text_sms, text_to_insert=text_to_insert)
        await setting.admin_commands(photo="admin_panel.jpg")

    async def get_chats_list(self, user: User, message_id: int, type_menu: str, role: str = "admin"):
        """Get special menu for super-admin or admin"""
        if type_menu.startswith("_set_chat_"):
            type_menu = type_menu.replace("_set_chat_", "")
            if type_menu == "0":
                # 👫👫 Додати групу 👫👫
                await self.add_new_chat(user=user)
            else:
                chat_pk = int(type_menu)
                # Get chat settings
                await self.edit_sms_with_chat(user=user, chat_pk=chat_pk, role=role, message_id=message_id)
            return
        else:
            """type_menu = ':m" """
            # ⚙️ Мої групи ⚙️
            if user.telegram_id == sb_telegram_id:
                chats = await func_db.get_chats()
            else:
                chats = await func_db.get_chats(user_id=user.id)  # get all [Chat] or []
            if chats:
                """get 1 chat in 1 SNS"""
                for chat in chats:
                    buttons = []
                    admin = await func_db.get_user_by_id(user_id=chat.user_id)
                    chat_info = await get_chat_info(admin=admin, chat=chat, get_photo=True)
                    chat_data, text, photo = chat_info["chat_data"], chat_info["text"], chat_info["photo"]
                    buttons.append(b_chat_settings(role=role, chat_doc_id=chat.id))
                    buttons.append(b_remove_panel)
                    reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
                    if photo:
                        await bot.send_photo(
                            chat_id=user.telegram_id, caption=text, photo=photo, reply_markup=reply_markup
                        )
                        try:
                            os.remove(path=f"{media_file_path}images/chat_photo_{chat.id}.jpg")
                        except Exception as e:
                            logger.error(e)
                    else:
                        await bot.send_message(chat_id=user.telegram_id, text=text, reply_markup=reply_markup)
                    if len(chats) > 1 and chat != chats[-1]:
                        await asyncio_sleep(delay=1)
            else:
                text = "У вас немає груп 🤷"
                buttons = list()
                if role == "super" or user.telegram_id == sb_telegram_id:
                    buttons.append(b_add_group)
                buttons.append([InlineKeyboardButton(text="Головне меню ⤴️", callback_data="0:m")])
                reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
                try:
                    await bot.edit_message_caption(
                        chat_id=user.telegram_id, message_id=message_id, caption=text, reply_markup=reply_markup
                    )
                except TelegramBadRequest as e:
                    logger.error(e)  # "message is not modified"
                    photo = FSInputFile(path=f"{media_file_path}admin_panel.jpg")
                    await bot.send_photo(chat_id=user.telegram_id, caption=text, photo=photo, reply_markup=reply_markup)
                    await bot.delete_message(chat_id=user.telegram_id, message_id=message_id)

    async def edit_sms_with_chat(self, user: User, chat_pk: int, role: str, message_id: int):
        """Get chat settings"""
        chat = await func_db.get_chat_with_user(pk=chat_pk)
        admin = chat.user
        chat_info = await get_chat_info(admin=admin, chat=chat, get_photo=False)
        chat_data, text = chat_info["chat_data"], chat_info["text"]
        """ Додати панель налаштувань якщо статус активний і фото """
        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons_for_chat_settings(role=role, chat_doc_id=chat.id))
        await bot.send_message(chat_id=user.telegram_id, text=text, reply_markup=reply_markup)
        await bot.delete_message(chat_id=user.telegram_id, message_id=message_id)

    async def change_user_chat_status(self, admin: User, user_chat_pk: int):
        """Set UserChat.status True or False"""
        user_chat = await func_db.get_user_chat_with_user(user_chat_pk=user_chat_pk)
        user_chat.status = False if user_chat.status else True
        await func_db.doc_update(doc=user_chat)
        text = get_user_info(user=user_chat.user, user_chat=user_chat)
        await bot.send_message(chat_id=admin.telegram_id, text=text)


class SetChat:
    """Chat settings for Admins"""

    async def get_command(self, user: User, chat: Chat, command: str, callback_query: CallbackQuery = None):
        """Execute the admin command"""
        if command == "card":
            """ "💳 номер вашої карти 💳" - Запускаємо процес зміни номеру банківської карти"""
            card_number = chat.card_number
            text_sms = (
                f"<b>Номер вашої банківської картки, яка вказана для отримання внесків:</b>\n\n"
                f"<code>{card_number}</code>\n\nps: Якщо ви хочете змінити номер картки, натисніть"
                f" <b>Tak ✔️</b> у вас з'явиться спеціальна форма, не змінюйте її, "
                f"лише додайте інший номер картки."
            )
            text_to_insert = "\nnew card number:\n"
            setting = Settings(telegram_id=user.telegram_id, text_sms=text_sms, text_to_insert=text_to_insert)
            await setting.admin_commands(photo="bank_card.jpg")
        elif command == "users":
            """ "🧔🏼 Користувачі чатів 👨‍🦱": Повертаємо дані про користувачів чату"""
            chat_users = await func_db.get_all_users_from_chat(chat_id=chat.id)
            chat_info = await get_chat_info(admin=user, chat=chat, get_photo=False)
            text = f"{chat_info.get('text')}"
            text_users = "\n<b>Зареєстровані користувачі чату:</b>" if chat_users else ""
            sms_list, sms_text = [], ""
            for n, user_chat in enumerate(start=1, iterable=chat_users):
                user_info = get_user_info(user=user_chat.user, user_chat=user_chat)
                sms_text += f"\n------------\n{user_info}"
                if n % 5 == 0:
                    sms_list.append(sms_text)
                    sms_text = ""
            if sms_text:
                sms_list.append(sms_text)
            for n, sms in enumerate(start=1, iterable=sms_list):
                text = text + text_users + sms if n == 1 else sms
                await bot.send_message(chat_id=user.telegram_id, text=text)
                await asyncio_sleep(delay=1)
        elif command == "report":
            """ "💰 Звіт по внескам 💰": Звіт про надходження коштів від користувачів чату"""
            title = await DataAI().get_title(chat=chat)
            sms_list, is_report = list(), False
            users_chats: List[UserChat] = await func_db.get_all_users_from_chat(chat_id=chat.id)
            for user_chat in users_chats:
                holiday: Optional[Holiday] = await func_db.get_holiday(user_pk=user_chat.user.id, chat_pk=chat.id)
                if holiday and holiday.status:
                    b_user: Optional[User] = await func_db.get_doc_by_id(model="user", doc_id=holiday.user_id)
                    if b_user:
                        text_chat = (
                            f"чат: <b>{title}</b>\n{user_data(user=b_user, is_birthday=True)}"
                            f"\nсума внеску: <b>{holiday.amount}</b>"
                        )
                    else:
                        text_chat = (
                            f"чат: <b>{title}</b>\n"
                            f"<u>Іменинник/іменинниця:</u>\n{holiday.info}\n"
                            f"Дата Народження: <code>{holiday.date_event}</code>\n"
                            f"сума внеску: <b>{holiday.amount}</b>"
                        )
                    sms_list.append(text_chat)
                    text_sms, number = str(), 0
                    for user_ch in users_chats:
                        report: Optional[Report] = await func_db.get_report(
                            user_pk=user_ch.user.id, chat_pk=chat.id, holiday_pk=holiday.id
                        )
                        if report:
                            number += 1
                            is_report = True
                            text_payment = await text_payment_info_with_set_link(report=report, user_chat=user_ch)
                            text_sms += f"\n----------\n{text_payment}"
                            if number % 5 == 0:
                                sms_list.append(text_sms)
                                text_sms = str()
                    if text_sms:
                        sms_list.append(text_sms)
            if sms_list:
                for sms in sms_list:
                    if not is_report and sms == sms_list[-1]:
                        """Не має звітів по користувачам чату"""
                        sms = f"{sms}\n\n<b>На даний момент немає боргів серед користувачів чату.</b>"
                    try:
                        await bot.send_message(chat_id=user.telegram_id, text=sms)
                        await asyncio_sleep(delay=1)
                    except Exception as e:
                        logger.error(str(e))
                        await asyncio_sleep(delay=5)
                        await bot.send_message(chat_id=user.telegram_id, text=sms)
            else:
                text = f"На даний момент немає боргів серед користувачів чату: {title}."
                await callback_query.answer(text=text, show_alert=True)
        elif command == "change_admin":
            """ "☢️ Передати права адміна ☣️": Запускаємо процес зміни адміна чату"""
            text_sms = (
                f"Якщо ви хочете передати свої повноваження адміністратора збору внесків "
                f"натисніть <b>Tak ✔️</b>, у вас буде спеціальна форма, не змінюйте її, "
                f"просто додайте номер телефону нового адміністратора у форматі: <b>+380...</b>"
            )
            text_to_insert = f"\nadmin for chat-{chat.id}:\n"
            setting = Settings(telegram_id=user.telegram_id, text_sms=text_sms, text_to_insert=text_to_insert)
            await setting.admin_commands(photo="new_admin.jpg")


class SetEvent:
    """Event settings"""

    async def get_command(self, user: User, holiday: Holiday, command: str, callback_query: CallbackQuery = None):
        """Get command from admin"""
        if command == "amount":
            text_sms = (
                f"Якщо ви хочете налаштувати іншу суму внеску для учасників чату, натисніть <b>Tak ✔️</b>, "
                f"у вас буде спеціальна форма, не змінюйте її, просто напишіть лише нову суму (грн)"
            )
            text_to_insert = f"\nset amount event-{holiday.id}:\n"
            setting = Settings(telegram_id=user.telegram_id, text_sms=text_sms, text_to_insert=text_to_insert)
            await setting.admin_commands(photo="new_event.jpg")
        elif command == "status":
            """Change holiday.status"""
            chat: Chat = holiday.chat
            holiday.status = False if holiday.status else True
            holiday: Holiday = await func_db.doc_update(doc=holiday)
            await callback_query.answer(text="Статус події змінено!", show_alert=True)
            await callback_query.message.delete()
            await panel_set_holidays(chat=chat, holiday=holiday)


class Settings:
    """class to create menu for setting to admin | super-admin"""

    def __init__(self, telegram_id: int, text_to_insert: str, text_sms: str):
        self.telegram_id = telegram_id
        self.text_to_insert = text_to_insert
        self.text_sms = text_sms

    async def admin_commands(self, photo: str = None):
        """
        :param photo: Optional[str]: example: 'admin_panel.jpg'
        """
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[buttons_for_admin_command(text_to_insert=self.text_to_insert)]
        )
        if photo:
            try:
                photo = FSInputFile(path=f"{media_file_path}{photo}")
                await bot.send_photo(
                    chat_id=self.telegram_id, caption=self.text_sms, photo=photo, reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(e)
                await bot.send_message(chat_id=self.telegram_id, text=self.text_sms, reply_markup=reply_markup)
        else:
            await bot.send_message(chat_id=self.telegram_id, text=self.text_sms, reply_markup=reply_markup)
