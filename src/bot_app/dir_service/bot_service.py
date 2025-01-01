import aiohttp
from PIL import Image
from io import BytesIO
from typing import Optional, Dict, Union, Any
from aiogram.types import (FSInputFile, ChatMember, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove,
                           ForceReply)
from aiogram.enums import ChatMemberStatus
import os
from config import media_file_path, bot_link
from src.bot_app.create_bot import bot
from src.bot_app.dir_menu.buttons_for_menu import b_my_groups
from src.sql.models import User, Chat, UserChat
from src.sql.func_db import doc_update, get_chats, get_user_chat, create_new_doc, get_chat_with_user, get_user_by_phone
from src.service.service_tools import correct_time, validate_phone
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)


async def check_user_in_group(telegram_id: int, chat_id: int) -> bool:
    """ Check user: is he member of the chat """
    try:
        # Отримання інформації про учасника групи
        member: ChatMember = await bot.get_chat_member(chat_id=chat_id, user_id=telegram_id)
        # Перевірка статусу учасника
        if member.status in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR}:
            logger.info(f"User: '{telegram_id}' is member of chat: {chat_id}")
            return True
        else:
            logger.info(f"User: '{telegram_id}' is NOT member of chat: {chat_id}")
            return False
    except Exception as e:
        logger.error(e)
        return False


async def check_user_in_every_chat(user: User) -> Dict[str, int]:
    """ Check: is User member of one or more chats """
    logger.info(f"start check_user_in_every_chat for user: {user.telegram_id}, {user.first_name}")
    new_user_chat, updated_user_chat = 0, 0
    chats = await get_chats()
    for chat in chats:
        if await check_user_in_group(telegram_id=user.telegram_id, chat_id=chat.chat_id):
            user_chat = await get_user_chat(chat_id=chat.id, user_telegram_id=user.telegram_id)
            if user_chat:
                # user_chat.status = True
                user_chat.updated_at = correct_time()
                r = await doc_update(doc=user_chat)
                updated_user_chat = updated_user_chat + 1 if r else updated_user_chat
            else:
                user_chat = {"chat_id": chat.id, "user_telegram_id": user.telegram_id, "status": True}
                r = await create_new_doc(model='user_chat', data=user_chat, data_has_datatime=False)
                new_user_chat = new_user_chat + 1 if r else new_user_chat
    res = {"new_user_chat": new_user_chat, "updated_user_chat": updated_user_chat}
    logger.info(str(res))
    return res


async def get_chat_info(
        admin: User, chat: Chat, get_photo: bool = True) -> Dict[str, Optional[Union[str, FSInputFile]]]:
    """ Get chat info from Telegram and DataBase """
    try:
        chat_data = await bot.get_chat(chat_id=chat.chat_id)
    except Exception as e:
        logger.error(e)
        chat_data = None
    status = await check_user_in_group(telegram_id=admin.telegram_id, chat_id=chat.chat_id)
    if chat.status != status:
        chat.status = status
        chat = await doc_update(doc=chat)
    status_description = "ГРУПА АКТИВНА" if status \
        else "<b>⚠️ налаштування не можливі - адмін або Телеграм бот не мають доступу до групи</b>"
    count_users = "не відомо"
    try:
        if status:
            count_users = await bot.get_chat_member_count(chat_id=chat.chat_id) - 1  # віднімаємо Телеграм-бота
    except Exception as e:
        logger.error(e)
    title = f"<b>{chat_data.title}</b>\n" if chat_data else ""
    user_name = f"@{admin.username}\n" if admin.username else ""
    text = (f"chat_id: <code>{chat.chat_id}</code>\nстатус: {status_description}\n{title}"
            f"кількість учасників: <b>{count_users}</b>\n<b>Адмін</b>\nІм'я в Телеграмі: "
            f"<b>{admin.first_name}</b>\nтелефон: <code>{admin.phone_number}</code>\n{user_name}")
    photo = None
    if get_photo:
        try:
            if chat_data:
                if chat_data.photo:
                    # Отримуємо інформацію про файл
                    file_info = await bot.get_file(chat_data.photo.big_file_id)
                    # Завантажуємо файл на локальний диск
                    file_path = f"{media_file_path}images/chat_photo_{chat.id}.jpg"
                    await bot.download_file(file_info.file_path, file_path)
                    # Використовуємо об'єкт FSInputFile для відправки фото з локального диску
                    photo = FSInputFile(file_path)
        except Exception as e:
            logger.error(e)
    return {"text": text, "chat_data": chat_data, "photo": photo, "title": title}


def get_user_info(user: User, user_chat: UserChat = None) -> str:
    """ Get user info from User """
    username = f"@{user.username}\n" if user.username else ""
    phone_number = f"телефон <code>{user.phone_number}</code>\n" if user.phone_number else ""
    if user_chat is None:
        birthday = str(user.birthday)[5:] if user.birthday else 'дані не внесені'
        birthday = f"день народження (month-day): <code>{birthday}</code>"
        link_settings = ""
    else:
        birthday = user.birthday if user.birthday else 'дані не внесені'
        birthday = f"день народження: <code>{birthday}</code>"
        desc = "<b>💲 задіяний до зборів</b>" if user_chat.status else "<b>🙅 не задіяний до зборів</b>"
        link_settings = f"\n{desc} <a href='{bot_link}?start=set-status-{user_chat.id}'>змінити</a>"
    text = f"<b>{user.first_name}</b>\n{username}{phone_number}{birthday}{link_settings}"
    return text


async def download_and_compress_image(
        url: str, max_size: int = 5 * 1024 * 1024, filename: str = "compressed_image.jpg") -> Optional[str]:
    """ Завантажує та стискає зображення з URL та повертає шлях до тимчасового файлу """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    image = Image.open(BytesIO(image_data))
                    quality = 85  # Початкове значення якості стиснення

                    # Стискаємо зображення до потрібного розміру
                    while True:
                        output = BytesIO()
                        image.save(output, format='JPEG', quality=quality)
                        size = output.tell()
                        if size <= max_size or quality <= 10:
                            break
                        quality -= 5
                    # Зберігаємо стиснене зображення у тимчасовий файл
                    file = f"{media_file_path}/images/{filename}"
                    with open(file=file, mode='wb') as temp_file:
                        temp_file.write(output.getvalue())
                    return file
        except Exception as e:
            logger.error(f"Error downloading and compressing image {url}: {e}")
    return None


async def send_compressed_image(
        chat_id: int, url: str, caption: str=None, filename: str="compressed_image.jpg", disable_notification=True,
        reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]]=None
) -> bool:
    """Відправляє стиснене зображення через Telegram"""
    # temp_filename = "compressed_image.jpg" - Ім'я тимчасового файлу
    res = False
    file_path = await download_and_compress_image(url=url, filename=filename)
    if file_path:
        try:
            # Використовуємо FSInputFile для відправки через Telegram
            input_file = FSInputFile(file_path)
            await bot.send_photo(
                chat_id=chat_id, photo=input_file, caption=caption,
                reply_markup=reply_markup,
                disable_notification=disable_notification
            )
            res = True
        except Exception as e:
            logger.error(f"Error sending image: {e}")
        finally:
            """ Видаляємо тимчасовий файл """
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        logger.error("Failed to compress and send image.")
    return res


async def check_admin(chat_pk: int, telegram_id: int, phone_number: str) -> bool:
    """ Check new admin by phone_number """
    chat = await get_chat_with_user(pk=chat_pk)
    if await check_user_in_group(telegram_id=telegram_id, chat_id=chat.chat_id):
        phone_number = validate_phone(phone_number=phone_number)
        if phone_number:
            new_admin = await get_user_by_phone(phone_number=phone_number)
            if new_admin:
                if await check_user_in_group(
                        telegram_id=new_admin.telegram_id, chat_id=chat.chat_id):
                    text = (f"Вітаємо, {new_admin.first_name}!\nВи стали новим адміністратором цього чату: "
                            f"<code>{chat.chat_id}</code>. Налаштуйте свою банківську картку, щоб приймати внески "
                            f"від учасників чату.")
                    reply_markup = InlineKeyboardMarkup(inline_keyboard=[b_my_groups(role='admin')])
                    photo = FSInputFile(path=f"{media_file_path}wellcome_admin.png")
                    await bot.send_photo(
                        chat_id=new_admin.telegram_id, photo=photo, caption=text, reply_markup=reply_markup)
                    new_admin.info = 'admin' if not new_admin.info else new_admin.info
                    await doc_update(doc=new_admin)
                    chat.user_id = new_admin.id
                    await doc_update(doc=chat)
                    return True
                else:
                    raise ValueError("У чаті не знайдено жодного користувача з таким номером телефону!")
            else:
                raise ValueError("За цим номером телефону в базі даних немає користувачів!")
        else:
            raise ValueError("Не валідний номер телефону!")
    else:
        raise ValueError("Ви або Телеграм-бот не маєте доступу до чату!")


# import asyncio
# from config import telegram_sb
# url = 'https://uvaga.gov.ua/uk/asset/129568/1/1?129568/1'
# asyncio.run(send_compressed_image(chat_id=telegram_sb, url=url, caption='test'))