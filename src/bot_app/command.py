from asyncio import create_task as asyncio_create_task
from typing import List

from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command
from config import bot_user_name, sb_telegram_id
from src.bot_app.create_bot import dp, bot
from src.bot_app.dir_menu.menu import Menu, AdminMenu
from src.bot_app.dir_menu.send_panel import text_payment_info_with_set_link
from src.sql.func_db import check_user, update_phone_number, get_chats, get_doc_by_id, get_user_chat
from src.sql.models import Report, UserChat, Chat, User
from src.bot_app.dir_service.bot_service import check_user_in_every_chat
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)

menu = Menu()
admin_menu = AdminMenu()


@dp.message(Command(commands=["start"]))
async def start_command_handler(message: Message):
    """ Check User in DataBase and give him menu buttons """
    chat_id = message.chat.id
    telegram_id = message.from_user.id
    if chat_id != telegram_id:
        """ User push '/start' command in group with bot """
        try:
            await message.reply(text=f"Напиши мені особисто:\n{bot_user_name}")
        except Exception as e:
            logger.error(e)
    else:
        """ User push '/start' command in private chat with bot """
        user = await check_user(message=message)
        if user:
            command_data = ["set-report-", "set-status-"]
            if (any(trigger in message.text for trigger in command_data) and
                    (user.info in ["admin", "super-admin"] or user.telegram_id==sb_telegram_id)):
                admin_chats: List[Chat] = await get_chats(user_id=user.id)
                check_admin = False
                if "set-status-" in message.text:
                    """ Admin change user_chat.status """
                    # https://t.me/holiday_organizer_bot?start=set-status-{user_chat_id}
                    user_chat_pk = int(message.text.split("set-status-")[-1])
                    user_chat: UserChat = await get_doc_by_id(model='user_chat', doc_id=user_chat_pk)
                    for chat in admin_chats:
                        if chat.id == user_chat.chat_id:
                            check_admin = True
                            break
                    if check_admin:
                        await admin_menu.change_user_chat_status(admin=user, user_chat_pk=user_chat_pk)
                elif "set-report-" in message.text:
                    """ Admin change report.status """
                    # https://t.me/holiday_organizer_bot?start=set-report-{report_id}
                    report_id = int(message.text.split("set-report-")[-1])
                    report: Report = await get_doc_by_id(model='report', doc_id=report_id)
                    chat: Chat = await get_doc_by_id(model='chat', doc_id=report.chat_id)
                    for chat_ in admin_chats:
                        if chat_.id == chat.id:
                            check_admin = True
                            break
                    if check_admin:
                        user_to_change: User = await get_doc_by_id(model='user', doc_id=report.user_id)
                        user_chat: UserChat = await get_user_chat(
                            chat_id=chat.id, user_telegram_id=user_to_change.telegram_id)
                        text = await text_payment_info_with_set_link(
                            report=report, user_chat=user_chat, user=user_to_change)
                        await bot.send_message(chat_id=user.telegram_id, text=text)
            else:
                await menu.start_command(user=user, message_text=message.text)
                task = asyncio_create_task(check_user_in_every_chat(user=user))
                ''' Запускаємо перевірку по користувачу - чи належить він до якихось чатів, які у нас є в базі. '''
                logger.info(f"asyncio_create_task(check_user_in_every_chat for user: {user.telegram_id}): {task}")
            await message.delete()


@dp.message(F.content_type == 'contact')
async def get_phone_number(message: Message):
    """ Get phone_number from User """
    phone_number = message.contact.phone_number
    telegram_id = message.contact.user_id
    await bot.send_message(chat_id=telegram_id, text=f'{phone_number}\n✔️')
    phone_number = f"+{phone_number}" if phone_number[0] != '+' else phone_number
    user = await update_phone_number(telegram_id=telegram_id, phone_number=phone_number)
    if user:
        logger.info(f'User:{telegram_id} gave his phone:{phone_number}')
        try:
            await bot.delete_message(chat_id=telegram_id, message_id=message.message_id)
            await bot.delete_message(chat_id=telegram_id, message_id=message.reply_to_message.message_id)
        except Exception as e:
            logger.error(e)
        if user.birthday:
            await menu.get_main_menu(user=user)
        else:
            await menu.request_birthday(user=user)