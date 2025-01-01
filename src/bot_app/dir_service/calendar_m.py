from typing import List

from src.sql.models import User
from src.sql.complex_func_db import get_intersecting_users
from src.bot_app.dir_service.bot_service import get_user_info
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)


async def get_schedule_holidays(user: User) -> List[str]:
    """ User get Date Birthdays the users of his chats """
    calendar_list = list()
    users = await get_intersecting_users(telegram_id=user.telegram_id)
    if user not in users:
        users.append(user)
    sorted_users = sorted(users, key=lambda doc: (doc.birthday.month, doc.birthday.day))
    if len(sorted_users) < 7:
        text = "".join(f"\n{get_user_info(user=doc, user_chat=None)}\n ------------" for doc in sorted_users)
        calendar_list.append(text)
    else:
        text = ""
        for n, doc in enumerate(start=1, iterable=sorted_users):
            text += f"\n{get_user_info(user=doc, user_chat=None)}\n ------------"
            if n % 7 == 0:
                calendar_list.append(text)
                text = ""
        if text:
            calendar_list.append(text)
    return calendar_list



async def testing():
    """Testing this module."""
    from src.sql.func_db import get_user_by_telegram_id
    from config import sb_telegram_id
    user = await get_user_by_telegram_id(telegram_id=sb_telegram_id)
    list_calendar = await get_schedule_holidays(user=user)
    [print(text) for text in list_calendar]

# import asyncio
# asyncio.run(main=testing())