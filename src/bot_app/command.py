from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command
from src.bot_app.create_bot import dp, bot
from src.bot_app.menu import Menu
from src.sql.func_db import check_user, update_phone_number
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)

menu = Menu()


@dp.message(Command(commands=["start"]))
async def start_command_handler(message: Message):
    """ Check User in DataBase and give him menu buttons """
    user = await check_user(message=message)
    if user:
        await menu.start_command(user=user)
        await message.delete()


@dp.message(F.content_type == 'contact')
async def get_phone_number(message: Message):
    """ Get phone_number from User """
    phone_number = message.contact.phone_number
    await message.reply(text=f'{phone_number}\n✔️')
    telegram_id = message.contact.user_id
    if phone_number[0] != '+':
        phone_number = f"+{phone_number}"
    user = await update_phone_number(telegram_id=telegram_id, phone_number=phone_number)
    if user:
        logger.info(f'User:{telegram_id} gave his phone:{phone_number}')
        await bot.delete_message(chat_id=telegram_id, message_id=message.message_id)
        await bot.delete_message(chat_id=telegram_id, message_id=message.reply_to_message.message_id)
        if user.birthday:
            await menu.give_main_menu(user=user)
        else:
            await menu.request_birthday(user=user)