from asyncio import sleep as asyncio_sleep
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from config import HOST, media_file_path
from src.bot_app.create_bot import bot
from src.sql.models import User
from src.sql.func_db import get_login_user_by_telegram_id
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
        text = "Поділиться своїм номером телефону за допомогою кнопкою нижче 👇"
        b_contact = KeyboardButton(text='поділитися контактом', request_contact=True)
        reply_markup = ReplyKeyboardMarkup(keyboard=[[b_contact]], resize_keyboard=True, one_time_keyboard=True)
        await bot.send_message(chat_id=user.telegram_id, text=text, reply_markup=reply_markup)

    async def request_birthday(self, user: User):
        """ Робимо запит на отримання даних про день народження: sms + miniapp """
        user_login = await get_login_user_by_telegram_id(telegram_id=user.telegram_id)
        if not user_login:
            return
        web_app = {'url': f"{HOST}/path/login/{user.telegram_id}/{user_login.password}"}
        text = "Вказати свій День Народження"
        text_b = "🎂 🥳 🎉"
        reply_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text_b, web_app=web_app)],])
        await bot.send_message(chat_id=user.telegram_id, text=text, reply_markup=reply_markup)

    async def get_main_menu(self, user: User, message_text: str = None, pause: int | float = None):
        """ Даємо користувачу головне меню """
        buttons = []
        ''' menu for everybody (data users) '''
        buttons.append([InlineKeyboardButton(text="⚒ Змінити свій 🎂 🛠", callback_data=f"0:user1")])
        buttons.append([InlineKeyboardButton(text="📅 Календар подій 📅", callback_data=f"0:user2")])
        buttons.append([InlineKeyboardButton(text="💵 Зробити внесок 💵", callback_data=f"0:user3")])
        if user.info in ['admin', 'super-admin']:
            ''' add menu for admin and super-admin (check users) '''
            buttons.append([InlineKeyboardButton(text="💰 Звіт по внескам 💰", callback_data=f"0:admin1")])
            buttons.append([InlineKeyboardButton(text="🎆 Створити подію 🎇", callback_data=f"0:admin2")])
            buttons.append([InlineKeyboardButton(text="Передати права адміна", callback_data=f"0:admin3")])
            if user.info == 'super-admin':
                ''' add menu for super-admin (add new group) '''
                buttons.append([InlineKeyboardButton(text="⚙️ керувати групами ⚙️", callback_data="0:super1")])
                # buttons.append([InlineKeyboardButton(text=" bla-bla ", callback_data="0:super2")])
        buttons.append([InlineKeyboardButton(text="🫣 сховати панель 🫣", callback_data="0:x")])
        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        photo = FSInputFile(path=f"{media_file_path}admin_panel.jpg")
        text = f"Привіт, {user.first_name}!"
        if pause and isinstance(pause, (int, float)):
            await asyncio_sleep(delay=pause)
        try:
            await bot.send_photo(chat_id=user.telegram_id, caption=text, photo=photo, reply_markup=reply_markup)
        except Exception as e:
            logger.error(e)
            await bot.send_message(chat_id=user.telegram_id, text=text, reply_markup=reply_markup)

