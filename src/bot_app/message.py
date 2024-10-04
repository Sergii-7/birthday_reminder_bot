import os
from aiogram import F
from aiogram.types import Message, FSInputFile, InputMediaDocument
from config import sb_telegram_id
from src.bot_app.create_bot import bot, dp
from src.sql import func_db
from src.bot_app.menu import Menu
from config import file_log_fast_api, file_log_tel_bot
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)


@dp.message(F.content_type.in_({'text', 'photo', 'audio', 'voice', 'video', 'document'}))
async def working(message: Message):
    telegram_id, message_id = message.from_user.id, message.message_id
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
        else:
            user = await func_db.get_login_user_by_telegram_id(telegram_id=telegram_id)
            await Menu().start_command(user=user)
    await message.delete()
