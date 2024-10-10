import os
import re
from aiogram import F
from aiogram.types import Message, FSInputFile, InputMediaDocument
from config import sb_telegram_id, bot_user_name
from src.service.service_tools import check_card_number
from src.bot_app.bot_service import check_user_in_group
from src.bot_app.create_bot import bot, dp
from src.sql import func_db
from src.bot_app.menu import Menu
from config import file_log_fast_api, file_log_tel_bot, my_banc_card
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)


@dp.message(F.content_type.in_({'text', 'photo', 'audio', 'voice', 'video', 'document'}))
async def working(message: Message):
    telegram_id, chat_id = message.from_user.id, message.chat.id
    if chat_id != telegram_id:
        """ User sent message in group with bot """
        return
    message_id, del_msg, menu = message.message_id, True, Menu()
    user = await func_db.get_user_by_telegram_id(telegram_id=telegram_id)
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
                if "new card number:" in data:
                    """ Update card_number """
                    data = data.replace("new card number:", "").strip()
                    # Використовуємо регулярний вираз для видалення всього, окрім цифр
                    card_number = re.sub(r"\D", "", data)
                    res = check_card_number(card_number=card_number)  # Check card_number
                    if res and len(card_number) == 16:
                        chats = await func_db.get_chats(user_id=user.id)
                        if chats:
                            del_msg = False
                            for chat in chats:
                                chat.card_number = card_number
                                await func_db.doc_update(doc=chat)
                            await message.reply(text=success_msg)
                        else:
                            text = "Ви не маєте повноважень приймати внески 🤷"
                            await bot.send_message(chat_id=telegram_id, text=text)
                            if telegram_id != sb_telegram_id:
                                user.info = None
                                user = await func_db.doc_update(doc=user)
                    else:
                        del_msg = False
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
                    else:
                        user.info = None
                        user = await func_db.doc_update(doc=user)
                elif "event for chat-{chat.id}:" in data:
                    """ Add new event for chat """
                    if user.info == "admin" or telegram_id == sb_telegram_id:
                        data = data.split("event for chat-")
                        del_msg = False
                        try:
                            chat_doc_id = int(data[0].split(":")[0])
                            event = "".join(data[1:])
                            print(chat_doc_id, event)
                            await message.reply(text=f"chat_doc_id: {chat_doc_id}, event:\n{event}")
                        except Exception as e:
                            await message.reply(text=f"{error_msg}:\n{e}")

    if del_msg:
        await message.delete()
        await menu.start_command(user=user)