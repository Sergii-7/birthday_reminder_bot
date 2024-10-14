import os, re
from typing import Optional
from aiogram import F
from aiogram.types import Message, FSInputFile, InputMediaDocument

from src.bot_app.dir_menu.send_panel import panel_set_holidays
from src.service.service_tools import check_card_number
from src.bot_app.dir_service.bot_service import check_user_in_group, check_admin
from src.bot_app.create_bot import bot, dp
from src.sql import func_db
from src.sql.models import Holiday, User, Chat
from src.bot_app.dir_menu.menu import Menu
from config import file_log_fast_api, file_log_tel_bot, my_banc_card, sb_telegram_id, bot_user_name, amount
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)
menu = Menu()


@dp.message(F.content_type.in_({'text', 'photo', 'audio', 'voice', 'video', 'document'}))
async def working(message: Message):
    telegram_id, chat_id = message.from_user.id, message.chat.id
    if chat_id != telegram_id:
        """ User sent message in group with bot """
        return
    message_id, del_msg = message.message_id, True
    user: User = await func_db.get_user_by_telegram_id(telegram_id=telegram_id)
    if message.text:
        if message.text == 'log' and telegram_id == sb_telegram_id:
            log_files = [file_log_fast_api, file_log_tel_bot]  # Список файлів з логами
            try:
                non_empty_files = [file for file in log_files if os.path.getsize(file) > 0]
                media = [InputMediaDocument(media=FSInputFile(log_file)) for log_file in non_empty_files]
                await bot.send_media_group(chat_id=telegram_id, media=media)
            except Exception as e:
                logger.error(e)
                for log_file_ in log_files:
                    input_file = FSInputFile(path=log_file_)
                    try:
                        await bot.send_document(chat_id=telegram_id, document=input_file)
                    except Exception as e:
                        text = f"ERROR in sending file '{log_file_}':\n{e}"
                        await bot.send_message(chat_id=telegram_id, text=text)
        elif message.text.startswith(bot_user_name):
            """ Get commands from admin and super-admin """
            error_msg, success_msg = "Дані не валідні 🤬", "Дані оновлено ✌️"
            if user.info in ["admin", "super-admin"] or telegram_id == sb_telegram_id:
                data = message.text.replace(bot_user_name, "").strip()
                command_data = [
                    "new card number:", "new chat_id:", "admin for chat-", "set amount event-",
                ]
                if any(trigger in data for trigger in command_data):
                    del_msg = False
                    if "new card number:" in data:
                        """ Update card_number """
                        data = data.replace("new card number:", "").strip()
                        # Використовуємо регулярний вираз для видалення всього, окрім цифр
                        card_number = re.sub(r"\D", "", data)
                        res = check_card_number(card_number=card_number)  # Check card_number
                        if res and len(card_number) == 16:
                            chats = await func_db.get_chats(user_id=user.id)
                            if chats:
                                for chat in chats:
                                    chat.card_number = card_number
                                    await func_db.doc_update(doc=chat)
                                await message.reply(text=success_msg)
                            else:
                                del_msg = True
                                text = "Ви не маєте повноважень приймати внески 🤷"
                                await bot.send_message(chat_id=telegram_id, text=text)
                                if telegram_id != sb_telegram_id:
                                    user.info = None
                                    user = await func_db.doc_update(doc=user)
                        else:
                            await message.reply(text=error_msg)
                    elif "new chat_id:" in data:
                        """ Create new Chat """
                        if user.info == "super-admin" or telegram_id == sb_telegram_id:
                            data = data.replace("new chat_id:", "").strip()
                            del_msg = False
                            try:
                                chat_id = int(data)
                                res = await check_user_in_group(telegram_id=telegram_id, chat_id=chat_id)
                                if res:
                                    new_chat = {"chat_id": chat_id, "user_id": user.id,
                                                "card_number": my_banc_card, "status": True}
                                    new_chat_id = await func_db.create_new_doc(model='chat', data=new_chat)
                                    if new_chat_id:
                                        logger.info(f"new_chat_id={new_chat_id}")
                                        await message.reply(text=success_msg)
                                    else:
                                        logger.error(f"chat created: {new_chat_id} = {new_chat_id}")
                                        await message.reply(f"{error_msg}:\nЦей чат вже в базі даних.")
                                else:
                                    text = (f"{error_msg}:\nЩоб додати нову групу, ви та Telegrambot: {bot_user_name} "
                                            f"повинні бути учасниками цієї групи: {chat_id}")
                                    await message.reply(text=text)
                            except Exception as e:
                                await message.reply(text=f"{error_msg}:\n{e}")
                    elif "admin for chat-" in data:
                        """ Change admin """
                        data = data.replace("admin for chat-", "", 1)
                        try:
                            chat_pk = int(data[0].split(":")[0])
                            phone_number = "".join(data[2:]).strip()
                            if await check_admin(chat_pk=chat_pk, telegram_id=telegram_id, phone_number=phone_number):
                                await message.reply(text=success_msg)
                                if telegram_id != sb_telegram_id or user.info != "super-admin":
                                    user.info = None
                                    await func_db.doc_update(doc=user)
                        except Exception as e:
                            await message.reply(text=f"{error_msg}:\n{e}")
                    elif "set amount event-" in data:
                        """ Change amount for event """
                        data = data.replace("set amount event-", "", 1)
                        try:
                            data = data.split(':')
                            amount_data = int(data[0])
                            holiday_id = int(data[1])
                            holiday: Optional[Holiday] = await func_db.get_holiday_with_chat(holiday_id=holiday_id)
                            if holiday:
                                chat: Chat = holiday.chat
                                holiday.amount = amount_data
                                await func_db.doc_update(doc=holiday)
                                await message.reply(text=success_msg)
                                await panel_set_holidays(chat=chat, holiday=holiday)
                            else:
                                raise ValueError(f"Дані не валідні!")
                        except Exception as e:
                            await message.reply(text=f"{error_msg}:\n{e}")

    if del_msg:
        await message.delete()
        await menu.start_command(user=user)