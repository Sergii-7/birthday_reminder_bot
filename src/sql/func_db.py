from typing import Optional, Union
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from src.sql.connect import DBSession
from src.sql.models import User, UserLogin, Chat, Holiday
from src.service.service_tools import correct_time
from src.service.loggers.py_logger_fast_api import get_logger

logger = get_logger(__name__)

models = {'user': User, 'user_login': UserLogin, 'chat': Chat, 'holiday': Holiday}


async def check_user(message: object) -> Optional[User]:
    """ Create User and UserLogin in DataBase """
    for n in range(3):
        try:
            logger.debug(f'check_user(telegram_id={message.from_user.id})')
            # Перевірка чи є користувач у базі даних
            async with DBSession() as session:
                async with session.begin():
                    result = await session.execute(select(User).filter_by(telegram_id=message.from_user.id))
                    user = result.scalar()
                    if user is None:
                        # Створення нового користувача
                        user = User(
                            telegram_id=message.from_user.id,
                            first_name=message.from_user.first_name,
                            last_name=message.from_user.last_name,
                            username=message.from_user.username,
                            language_code=message.from_user.language_code
                        )
                        session.add(user)
                        user_login = UserLogin(
                            user_telegram_id=user.telegram_id
                        )
                        session.add(user_login)
                        logger.info(f"Kyiv_time: {correct_time()} add new_user in db: telegram_id={user.telegram_id}")
                    return user
        except Exception as e:
            logger.error(f"attempt={n + 1} error: {e}")
    return None


async def get_user_by_login(telegram_id: int, password: str) -> Optional[Union[User, UserLogin]]:
    """ Get user and user login from DataBase by 'login' and 'password' """
    for n in range(3):
        try:
            logger.debug(f'get_user_by_login(telegram_id={telegram_id}, password=***)')
            async with DBSession() as session:
                result = await session.execute(
                    select(UserLogin)
                    .options(joinedload(UserLogin.user))  # Завантажуємо пов'язаний об'єкт User
                    .filter(UserLogin.user_telegram_id == telegram_id, UserLogin.password == password)
                )
                user_login = result.scalar()
                if user_login:
                    return user_login  # `user_login` тепер містить `User` як атрибут `user_login.user`
                else:
                    return None
        except Exception as e:
            logger.error(f"attempt={n + 1} error: {e}")
    return None


async def get_login_user_by_telegram_id(telegram_id: int) -> Optional[UserLogin]:
    """ Get user and user login from DataBase by 'login' and 'password' """
    for n in range(3):
        try:
            logger.debug(f'get_login_user_by_telegram_id(telegram_id={telegram_id})')
            async with DBSession() as session:
                result = await session.execute(select(UserLogin).filter_by(user_telegram_id=telegram_id))
                user_login = result.scalar()
                if user_login:
                    return user_login
                else:
                    return None
        except Exception as e:
            logger.error(f"attempt={n + 1} error: {e}")
    return None


async def update_phone_number(telegram_id: int, phone_number: str) -> Optional[Union[User]]:
    """ Update 'phone_number' in table='users' in DataBase """
    for n in range(3):
        try:
            logger.debug(f'update_phone_number(telegram_id={telegram_id}, phone_number={phone_number})')
            async with DBSession() as session:
                async with session.begin():
                    user = await session.execute(select(User).filter_by(telegram_id=telegram_id))
                    user = user.scalar()
                    if user:
                        # Оновити дані користувача
                        user.phone_number = phone_number
                        await session.commit()
                        return user
                    else:
                        logger.error(f'User with phone_number={phone_number} is empty in DataBase')
                        return None
        except Exception as e:
            logger.error(f"attempt={n + 1} error: {e}")
    return None


async def doc_update(
        doc: Union[User, UserLogin, Chat, Holiday]) -> Union[bool, Union[User, UserLogin, Chat, Holiday]]:
    """ Оновлюємо будь-який object в якому ми робили ті чи інші зміни """
    if doc:
        for n in range(3):
            try:
                logger.debug(f'doc_update(doc={doc})')
                async with DBSession() as session:
                    async with session.begin():
                        await session.merge(doc)
                        await session.commit()
                        return doc
            except Exception as e:
                logger.error(f'Attempt {n + 1} failed: {e}')
    return False