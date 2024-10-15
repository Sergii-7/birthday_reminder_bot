from asyncio import create_task
from datetime import date, timedelta
from typing import Optional

from config import amount
from src.bot_app.dir_menu.send_panel import panel_set_holidays
from src.dir_schedule.some_tools import AskingMoney, GreetingsUser
from src.sql.func_db import get_chats, get_all_users_from_chat, get_holiday, create_new_doc, get_doc_by_id
from src.sql.models import Chat, Holiday
from src.service.service_tools import correct_time
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)


class BackgroundTask:
    """Class for start background task"""
    def __init__(self):
        pass

    async def check_users_birthday(self, days_to_birthday: int = 10):
        """Check users birthdays in DataBase, send sms for chat members - start one time per day"""
        logger.info(f">>> check_users_birthday()")
        date_today_str = str(correct_time())[:10]
        date_today: date = date.fromisoformat(date_today_str)
        to_birthday_list = [{n: str(date_today + timedelta(days=n))[5:]} for n in range(days_to_birthday + 1)]
        chats = await get_chats(status=True)
        for chat in chats:
            """Get all users from chat"""
            users_chats = await get_all_users_from_chat(chat_id=chat.id)
            for user_chat in users_chats:
                if user_chat.status:
                    """If user take part of chat party - якщо він приймає участь у зборі внесків"""
                    user = user_chat.user
                    if user.birthday:
                        for data_birthday in to_birthday_list:
                            for key, value in data_birthday.items():
                                days_to_birthday: int = key  # 0 | 1 | 2 ...
                                birthday_str: str = value    # '10-19'
                                if str(user.birthday)[5:] == birthday_str:
                                    if days_to_birthday == 0:
                                        """User has birthday today - AI sends greetings to the user personally 
                                        and in the group"""
                                        logger.info(f"user: {user.first_name}|{user.telegram_id} has birthday today.")
                                        greet_user = GreetingsUser()
                                        try:
                                            task = create_task(greet_user.start_greet(user_chat=user_chat))
                                            logger.info(f"GreetingsUser().start_greet(): {task}")
                                        except Exception as e:
                                            logger.error(e)
                                    else:
                                        chat: Chat = await get_doc_by_id(model='chat', doc_id=user_chat.chat_id)
                                        holiday: Optional[Holiday] = await get_holiday(
                                            user_pk=user.id, chat_pk=chat.id)
                                        if not holiday:
                                            """По дефолту новий holiday.status=True, тобто подія активна, 
                                            щоб інші користувачі НЕ отримували СМС з проханням зробити внесок
                                            - Адмін має ЗАКРИТИ подію"""
                                            info = f"<b>{user.first_name}</b>\n<code>{user.phone_number}</code>"
                                            holiday_data = {
                                                "user_id": user.id, "chat_id": chat.id, "status": True,
                                                "date_event": user.birthday, "amount": amount, "info": info
                                            }
                                            await create_new_doc(model='holiday', data=holiday_data)

                                        holiday: Holiday = await get_holiday(user_pk=user.id, chat_pk=chat.id)
                                        """Send panel for Admin to set Holiday in DataBase"""
                                        await panel_set_holidays(chat=chat, holiday=holiday)

                                        if days_to_birthday < 8:
                                            """ days_to_birthday < 8 """
                                            if holiday.status:
                                                """ Подія активна """
                                                """User has birthday in int: 'days_to_birthday' - we send another users 
                                                the admin card with request for transferring money"""
                                                logger.info(
                                                    f"user: {user.first_name}|{user.telegram_id} has birthday in "
                                                    f"{days_to_birthday} days."
                                                )
                                                money_asker = AskingMoney()
                                                try:
                                                    task = create_task(money_asker.start_asking(
                                                        birthday_user=user, users_chats=users_chats,
                                                        days_to_birthday=days_to_birthday, holiday=holiday)
                                                    )
                                                    logger.info(f"AskingMoney().send_asking(): {task}")
                                                except Exception as e:
                                                    logger.error(e)




# import asyncio
# background_task = BackgroundTask()
# asyncio.run(main=background_task.check_users_birthday(days_to_birthday=10))
