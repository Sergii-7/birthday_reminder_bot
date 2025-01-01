import asyncio
from typing import List
from sqlalchemy.future import select

from src.sql.connect import DBSession
from src.sql.models import User, UserChat
from src.service.loggers.py_logger_fast_api import get_logger

logger = get_logger(__name__)


async def get_intersecting_users(telegram_id: int) -> List[User]:
    """User get all users from their chats, where users have birthday set."""
    for n in range(3):
        try:
            logger.debug(f'get_intersecting_users(telegram_id={telegram_id})')
            async with DBSession() as session:
                chats_with_user = (
                    select(UserChat.chat_id)
                    .filter(UserChat.user_telegram_id == telegram_id)
                ).subquery()  # Виправлено: додаємо явний select()

                # Витягти всіх користувачів, які також беруть участь у тих самих чатах і у яких birthday не None
                stmt = (
                    select(User)
                    .join(UserChat, User.telegram_id == UserChat.user_telegram_id)
                    .filter(UserChat.chat_id.in_(select(chats_with_user)))  # Явно використовуємо select()
                    .filter(User.telegram_id != telegram_id)  # Виключити самого користувача
                    .filter(User.birthday.isnot(None))  # Додати фільтр для поля birthday
                )
                result = await session.execute(stmt)
                users_in_same_chats = result.scalars().all()
                # Забезпечити унікальність користувачів за допомогою set
                return list(set(users_in_same_chats))
        except Exception as e:
            logger.error(f"Attempt={n+1}: {e}")
            await asyncio.sleep(0.5)
    return []


