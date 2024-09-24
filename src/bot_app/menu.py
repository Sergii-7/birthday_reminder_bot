from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from config import HOST
from src.bot_app.create_bot import bot
from src.sql.models import User
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)


class Menu:
    """ Menu buttons """
    async def start_command(self, user: User):
        """ Перевіряємо користувача та або даємо йому головне меню або запитуємо у нього додаткові дані """
        if user.phone_number:
            if user.birthday:
                ''' Даємо користувачу головне меню '''
                await self.give_main_menu(user=user)
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

    async def give_main_menu(self, user: User):
        """ Даємо користувачу головне меню """

        reply_markup = None

        await bot.send_message(chat_id=user.telegram_id, text='main buttons', reply_markup=None)

    async def request_birthday(self, user: User):
        """ Робимо запит на отримання даних про день народження: sms + miniapp """

        reply_markup = None

        await bot.send_message(chat_id=user.telegram_id, text='main buttons', reply_markup=None)

