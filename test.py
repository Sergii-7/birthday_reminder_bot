import asyncio
from aiogram.types import FSInputFile
from config import sb_telegram_id, media_file_path
from src.bot_app.create_bot import bot


async def test():
    chat_id = -4546525808
    chat = await bot.get_chat(chat_id=chat_id)
    # chat = id=-4546525808 type='group' title='Тестовий чат для розробки ТБ' username=None first_name=None last_name=None is_forum=None accent_color_id=6 active_usernames=None available_reactions=None background_custom_emoji_id=None bio=None birthdate=None business_intro=None business_location=None business_opening_hours=None can_set_sticker_set=None custom_emoji_sticker_set_name=None description=None emoji_status_custom_emoji_id=None emoji_status_expiration_date=None has_aggressive_anti_spam_enabled=None has_hidden_members=None has_private_forwards=None has_protected_content=None has_restricted_voice_and_video_messages=None has_visible_history=None invite_link=None join_by_request=None join_to_send_messages=None linked_chat_id=None location=None message_auto_delete_time=None permissions=ChatPermissions(can_send_messages=True, can_send_audios=True, can_send_documents=True, can_send_photos=True, can_send_videos=True, can_send_video_notes=True, can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True, can_add_web_page_previews=True, can_change_info=True, can_invite_users=True, can_pin_messages=True, can_manage_topics=True, can_send_media_messages=True) personal_chat=None photo=ChatPhoto(small_file_id='AQADAgADZuIxGxlDAAFIAAgCAAOQhQHx_v___wAINgQ', small_file_unique_id='AQADZuIxGxlDAAFIAAE', big_file_id='AQADAgADZuIxGxlDAAFIAAgDAAOQhQHx_v___wAINgQ', big_file_unique_id='AQADZuIxGxlDAAFIAQ') pinned_message=None profile_accent_color_id=None profile_background_custom_emoji_id=None slow_mode_delay=None sticker_set_name=None unrestrict_boost_count=None max_reaction_count=11 can_send_paid_media=None all_members_are_administrators=True
    # Перевіряємо, чи є фото у чату
    if chat.photo:
        # Отримуємо інформацію про файл
        file_info = await bot.get_file(chat.photo.big_file_id)
        # Завантажуємо файл на локальний диск
        file_path = f"{media_file_path}images/chat_photo.jpg"
        await bot.download_file(file_info.file_path, file_path)
        # Використовуємо об'єкт FSInputFile для відправки фото з локального диску
        photo = FSInputFile(file_path)
        await bot.send_photo(chat_id=sb_telegram_id, photo=photo)
    else:
        print("Чат не має фотографії.")



# asyncio.run(test())


