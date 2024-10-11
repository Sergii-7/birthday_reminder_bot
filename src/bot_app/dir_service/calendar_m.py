from typing import List
from src.sql.models import User
from src.sql.complex_func_db import get_intersecting_users
from src.bot_app.dir_service.bot_service import get_user_info
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)


async def get_schedule_holidays(user: User) -> str:
    """ User get Date Birthdays the users of his chats """
    users = await get_intersecting_users(telegram_id=user.telegram_id)
    # users.append(user)
    if not users:
        users = [user]
    sorted_users = sorted(users, key=lambda user_doc: (user_doc.birthday.month, user_doc.birthday.day))
    text = "".join(f"\n{get_user_info(user=doc, calendar=True)}\n ------------" for doc in sorted_users)
    return text.strip()



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