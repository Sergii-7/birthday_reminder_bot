from asyncio import sleep as asyncio_sleep
from typing import List, Optional, Union, Dict, Any
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from config import HOST, media_file_path, get_chat_id_bot, sb_telegram_id
from src.bot_app.create_bot import bot
from src.sql.models import User, Chat
from src.bot_app.bot_service import get_chat_info
from src.sql import func_db
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)


class Menu:
    """ Menu buttons """

    async def start_command(self, user: User, message_text: str = None):
        """ Перевіряємо користувача та або даємо йому головне меню або запитуємо у нього додаткові дані """
        if user.phone_number:
            if user.birthday:
                ''' Даємо користувачу головне меню '''
                await self.get_main_menu(user=user, message_text=message_text)
            else:
                ''' Робимо запит на отримання даних про день народження: sms + miniapp '''
                await self.request_birthday(user=user)
        else:
            ''' Робимо запит на отримання номеру телефону користувача '''
            await self.request_phone_number(user=user)

    async def request_phone_number(self, user: User):
        """ Робимо запит на номер телефону """
        text: str = "Поділиться своїм номером телефону за допомогою кнопкою нижче 👇"
        b_contact = KeyboardButton(text='поділитися контактом', request_contact=True)
        reply_markup = ReplyKeyboardMarkup(keyboard=[[b_contact]], resize_keyboard=True, one_time_keyboard=True)
        await bot.send_message(chat_id=user.telegram_id, text=text, reply_markup=reply_markup)

    async def request_birthday(self, user: User):
        """ Робимо запит на отримання даних про день народження: sms + miniapp """
        user_login = await func_db.get_login_user_by_telegram_id(telegram_id=user.telegram_id)
        if not user_login:
            return
        web_app: Dict[str, str] = {'url': f"{HOST}/path/login/{user.telegram_id}/{user_login.password}"}
        text: str = "Вказати свій День Народження"
        text_b: str = "🎂 🥳 🎉"
        reply_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text_b, web_app=web_app)],])
        await bot.send_message(chat_id=user.telegram_id, text=text, reply_markup=reply_markup)

    async def get_main_menu(self, user: User, message_text: str = None, pause: int | float = None):
        """ Даємо користувачу головне меню """
        buttons = []
        ''' menu for everybody (data users) '''
        buttons.append([InlineKeyboardButton(text="🎂 Змінити дату ДР 🎂", callback_data=f"0:user1")])
        buttons.append([InlineKeyboardButton(text="📅 Календар подій 📅", callback_data=f"0:user2")])
        buttons.append([InlineKeyboardButton(text="💵 Зробити внесок 💵", callback_data=f"0:user3")])
        if user.info in ['admin', 'super-admin']:
            ''' add menu for admin and super-admin (check users) '''
            callback_data = '0:super:m' if (user.info=='super-admin' or
                                            user.telegram_id==sb_telegram_id) else '0:admin:m'
            buttons.append([InlineKeyboardButton(text="⚙️ Мої групи ⚙️", callback_data=callback_data)])

        buttons.append([InlineKeyboardButton(text="🫣 сховати панель 🫣", callback_data="0:x")])
        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        photo = FSInputFile(path=f"{media_file_path}admin_panel.jpg")
        text: str = f"Привіт, {user.first_name}!"
        if pause and isinstance(pause, (int, float)):
            await asyncio_sleep(delay=pause)
        await bot.send_photo(chat_id=user.telegram_id, caption=text, photo=photo, reply_markup=reply_markup)


class AdminMenu:
    """ Get menu for admin or super-admin """

    async def add_new_chat(self, user: User):
        """ Add new chat """
        text_sms: str = (f"Якщо ви бажаєте створити нову групу, натисніть <b>Tak ✔️</b> у вас з'явиться "
                         f"спеціальна форма, не змінюйте її, лише додайте chat_id цієї групи.\n"
                         f"ps: Дізнатися chat_id можна за допомогою цього бота: {get_chat_id_bot}")
        text_to_insert = '\nnew chat_id:\n'
        setting = Settings(telegram_id=user.telegram_id, text_sms=text_sms, text_to_insert=text_to_insert)
        await setting.admin_commands(photo="admin_panel.jpg")

    async def edit_sms_with_chat(self, user: User, type_menu: str, role: str, message_id: int):
        """ Get chat settings """
        buttons = list()
        chat_pk = int(type_menu)
        chat = await func_db.get_chat_with_user(pk=chat_pk)
        admin = chat.user
        chat_info = await get_chat_info(admin=admin, chat=chat)
        chat_data, text, photo = chat_info['chat_data'], chat_info['text'], chat_info['photo']
        """ Додати панель налаштувань якщо статус активний і фото """
        buttons.append([InlineKeyboardButton(
            text="💳 Номер вашої карти 💳", callback_data=f"0:{role}:set:card:{chat.id}")])
        buttons.append([InlineKeyboardButton(
            text="🧔🏼 Користувачі чатів 👨‍🦱", callback_data=f"0:{role}:set:users:{chat.id}")])
        buttons.append([InlineKeyboardButton(
            text="🎆 Створити подію 🎇", callback_data=f"0:{role}:set:holiday:{chat.id}")])
        buttons.append([InlineKeyboardButton(
            text="💰 Звіт по внескам 💰", callback_data=f"0:{role}:set:report:{chat.id}")])
        buttons.append([InlineKeyboardButton(
            text="☢️ Передати права адміна ☣️", callback_data=f"0:{role}:set:change_admin:{chat.id}")])
        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        try:
            await bot.edit_message_caption(
                chat_id=user.telegram_id, message_id=message_id, caption=text, reply_markup=reply_markup)
        except TelegramBadRequest as e:
            logger.error(e)  # "message is not modified"
            await bot.send_photo(chat_id=user.telegram_id, caption=text, photo=photo,
                                 reply_markup=reply_markup)
            await bot.delete_message(chat_id=user.telegram_id, message_id=message_id)

    async def get_chats_list(self, user: User, message_id: int, type_menu: str, role: str = "admin"):
        """ Get special menu for super-admin or admin """
        if type_menu.startswith("_set_chat_"):
            if type_menu == '0':
                # 👫👫 Додати групу 👫👫
                await self.add_new_chat(user=user)
            else:
                # Get chat settings
                await self.edit_sms_with_chat(user=user, type_menu=type_menu, role=role, message_id=message_id)
            return
        else:
            """ type_menu = ':m" """
            # ⚙️ Мої групи ⚙️
            chats = await func_db.get_chats()  # get all [Chat] or []
            if chats:
                ''' get 1 chat in 1 SNS '''
                for chat in chats:
                    buttons = []
                    admin = await func_db.get_user_by_id(user_id=chat.user_id)
                    chat_info = await get_chat_info(admin=admin, chat=chat)
                    chat_data, text, photo = chat_info['chat_data'], chat_info['text'], chat_info['photo']
                    button_text = f"{admin.first_name}" if not chat_data else chat_data.title
                    callback_data = f"0:{role}_set_chat_{chat.id}"
                    buttons.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])
                    reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
                    await bot.send_photo(chat_id=user.telegram_id, caption=text, photo=photo, reply_markup=reply_markup)
                    if len(chats) > 1 and chat != chats[-1]:
                        await asyncio_sleep(delay=1)
            else:
                text = "У вас немає груп 🤷"
                buttons = list()
                if role == "super":
                    buttons.append(
                        [InlineKeyboardButton(text="👫👫 Додати групу 👫👫", callback_data="0:super_set_chat_0")])
                buttons.append([InlineKeyboardButton(text="Головне меню ⤴️", callback_data="0:m")])
                reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
                try:
                    await bot.edit_message_caption(
                        chat_id=user.telegram_id, message_id=message_id, caption=text, reply_markup=reply_markup)
                except TelegramBadRequest as e:
                    logger.error(e)  # "message is not modified"
                    photo = FSInputFile(path=f"{media_file_path}admin_panel.jpg")
                    await bot.send_photo(
                        chat_id=user.telegram_id, caption=text, photo=photo, reply_markup=reply_markup)
                    await bot.delete_message(chat_id=user.telegram_id, message_id=message_id)


class Settings:
    """ class to create menu for setting to admin | super-admin """
    def __init__(self, telegram_id: int, text_to_insert: str, text_sms: str):
        self.telegram_id = telegram_id
        self.text_to_insert = text_to_insert
        self.text_sms = text_sms

    async def admin_commands(self, photo: str = None):
        """
        :param photo: (str) example: 'admin_panel.jpg'
        :return: None
        """
        b1 = InlineKeyboardButton(text="Tak ✔️", switch_inline_query_current_chat=self.text_to_insert)
        b2 = InlineKeyboardButton(text="Hi 🙅", callback_data="0:m")
        reply_markup = InlineKeyboardMarkup(inline_keyboard=[[b1, b2]])
        if photo:
            try:
                photo = FSInputFile(path=f"{media_file_path}{photo}")
                await bot.send_photo(
                    chat_id=self.telegram_id, caption=self.text_sms, photo=photo, reply_markup=reply_markup)
            except Exception as e:
                logger.error(e)
                await bot.send_message(chat_id=self.telegram_id, text=self.text_sms, reply_markup=reply_markup)
        else:
            await bot.send_message(chat_id=self.telegram_id, text=self.text_sms, reply_markup=reply_markup)
