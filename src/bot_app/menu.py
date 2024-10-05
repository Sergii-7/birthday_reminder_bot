from asyncio import sleep as asyncio_sleep
from typing import List, Optional, Union, Dict, Any
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from config import HOST, media_file_path, get_chat_id_bot
from src.bot_app.create_bot import bot
from src.sql.models import User, Chat
from src.bot_app.bot_service import check_user_in_group
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
            buttons.append([InlineKeyboardButton(text="💳 Номер вашої карти 💳", callback_data=f"0:admin1")])
            buttons.append([InlineKeyboardButton(text="🧔🏼 Користувачі чатів 👨‍🦱", callback_data=f"0:admin2")])
            buttons.append([InlineKeyboardButton(text="🎆 Створити подію 🎇", callback_data=f"0:admin3")])
            buttons.append([InlineKeyboardButton(text="💰 Звіт по внескам 💰", callback_data=f"0:admin4")])
            buttons.append([InlineKeyboardButton(text="☢️ Передати права адміна ☣️", callback_data=f"0:admin5")])
            if user.info == 'super-admin':
                ''' add menu for super-admin (add new group) '''
                buttons.append([InlineKeyboardButton(text="⚙️ керувати групами ⚙️", callback_data="0:super1")])
                # buttons.append([InlineKeyboardButton(text=" bla-bla ", callback_data="0:super2")])
        buttons.append([InlineKeyboardButton(text="🫣 сховати панель 🫣", callback_data="0:x")])
        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        photo = FSInputFile(path=f"{media_file_path}admin_panel.jpg")
        text: str = f"Привіт, {user.first_name}!"
        if pause and isinstance(pause, (int, float)):
            await asyncio_sleep(delay=pause)
        await bot.send_photo(chat_id=user.telegram_id, caption=text, photo=photo, reply_markup=reply_markup)

    async def for_super_admin(self, user: User, message_id: int, type_menu: str):
        """ Get special menu for super-admin """
        chats = await func_db.get_chats()  # get all [Chat] or []
        text: str = "Вибери групу."
        buttons = list()
        if chats:
            if type_menu.startswith("_set_chat_"):
                type_menu = type_menu.replace("_set_chat_", "")
                if type_menu == '0':
                    # 👫👫 Додати групу 👫👫
                    text_sms: str = (f"Якщо ви бажаєте створити нову групу, натисніть <b>Tak ✔️</b> у вас з'явиться "
                                     f"спеціальна форма, не змінюйте її, лише додайте chat_id цієї групи.\n"
                                     f"ps: Дізнатися chat_id можна за допомогою цього бота: {get_chat_id_bot}")
                    text_to_insert = '\nnew chat_id:\n'
                    setting = Settings(telegram_id=user.telegram_id, text_sms=text_sms, text_to_insert=text_to_insert)
                    await setting.admin_commands(photo="admin_panel.jpg")
                    return
                else:
                    ''' Get chat settings '''
                    chat_pk = int(type_menu)
                    chat = await func_db.get_chat_with_user(pk=chat_pk)
                    admin = chat.user
                    status = await check_user_in_group(telegram_id=chat.admin.telegram_id, chat_id=chat.chat_id)
                    if chat.status != status:
                        chat.status = status
                        chat = await func_db.doc_update(doc=chat)
                    status_description = "ГРУПА АКТИВНА" if status else ("<b>⚠️ налаштування не можливі - адмін або "
                                                                         "Телеграм бот не мають доступу до групи</b>")
                    count_users = await bot.get_chat_member_count(chat_id=chat.chat_id) if status else "не відомо"
                    chat_data = None if not status else await bot.get_chat(chat_id=chat.chat_id)
                    title = f"{chat_data.title}\n" if chat_data else ""
                    user_name = f"@{admin.username}\n" if admin.username else ""
                    text = (f"chat_id: <code>{chat.chat_id}</code>\nстатус: {status_description}\n<b>{title}</b"
                            f"кількість учасників: <b>{count_users}</b>\n\n<b>Адмін</b>\nІм'я в Телеграмі: "
                            f"<b>{admin.first_name}</b>\nтелефон: <code>{admin.phone_number}</code>\n{user_name}")

                    """ Додати панель налаштувань якщо статус активний і фото """
                    reply_markup = None
                    try:
                        photo = chat_data.photo.small_file_id
                    except Exception as e:
                        logger.error(e)
                        photo = FSInputFile(path=f"{media_file_path}admin_panel.jpg")
                    try:
                        await bot.edit_message_caption(
                            chat_id=user.telegram_id, message_id=message_id, caption=text, reply_markup=reply_markup)
                    except TelegramBadRequest as e:
                        logger.error(e)  # "message is not modified"
                        await bot.send_photo(chat_id=user.telegram_id, caption=text, photo=photo,
                                             reply_markup=reply_markup)
                        await bot.delete_message(chat_id=user.telegram_id, message_id=message_id)
                    return
            else:
                # ⚙️ керувати групами ⚙️
                index_2 = int(type_menu) * 10
                index_1 = index_2 - 10
                slice_chats = chats[index_1:index_2]
                if not slice_chats:
                    slice_chats = chats[:10]
                for n in range(len(slice_chats)):
                    chat = slice_chats[n]
                    admin = await func_db.get_user_by_id(user_id=chat.user_id)
                    button_text: str = f"{admin.first_name}:{admin.phone_number}"
                    callback_data: str = f"0:super_set_chat_{chat.id}"
                    buttons.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])
                if len(slice_chats) < len(chats):
                    if slice_chats[-1] == chats[-1]:
                        button_text: str = "Дивитися з початку ⬅️"
                        callback_data = "0:super1"
                    else:
                        button_text: str = "Дивитися далі ➡️"
                        callback_data = f"0:super{index_2/100+1}"
                    buttons.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])
                buttons.append(
                    [InlineKeyboardButton(text="👫👫 Додати групу 👫👫", callback_data="0:super_set_chat_0")])
        else:
            text: str = "У вас немає груп 🤷"
            buttons.append([InlineKeyboardButton(text="👫👫 Додати групу 👫👫", callback_data="0:super_set_chat_0")])
        buttons.append([InlineKeyboardButton(text="🫣 сховати панель 🫣", callback_data="0:x")])
        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        try:
            await bot.edit_message_caption(
                chat_id=user.telegram_id, message_id=message_id, caption=text, reply_markup=reply_markup)
        except TelegramBadRequest as e:
            logger.error(e)  # "message is not modified"
            photo = FSInputFile(path=f"{media_file_path}admin_panel.jpg")
            await bot.send_photo(chat_id=user.telegram_id, caption=text, photo=photo, reply_markup=reply_markup)
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
