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
    # users.append(user)
    if not users:
        users = [user]
    sorted_users = sorted(users, key=lambda user_doc: (user_doc.birthday.month, user_doc.birthday.day))
    if len(sorted_users) < 6:
        text = "".join(f"\n{get_user_info(user=doc, user_chat=None)}\n ------------" for doc in sorted_users)
        calendar_list.append(text)
    else:
        text = ""
        for n, doc in enumerate(start=1, iterable=users):
            text += f"\n{get_user_info(user=doc, calendar=True)}\n ------------"
            if n % 5 == 0:
                calendar_list.append(text)
                text = ""
        if text:
            calendar_list.append(text)
    return calendar_list



# async def test():
#     from config import sb_telegram_id
#     users = await get_intersecting_users(telegram_id=sb_telegram_id)
#     sorted_users = sorted(users, key=lambda x: (x.birthday.month, x.birthday.day))
#     sorted_users = sorted(users, key=lambda user_doc: (user_doc.birthday.month, user_doc.birthday.day))
#     text = "".join(f"\n{get_user_info(user=doc, calendar=True)}\n ------------" for doc in sorted_users)
#     print(text.strip())
#
# import asyncio
# asyncio.run(main=test())