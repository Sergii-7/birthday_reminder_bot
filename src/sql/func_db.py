from datetime import datetime
from typing import Optional, Union, List
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
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


async def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
    """ Get User from DataBase by telegram_id """
    for n in range(3):
        try:
            logger.debug(f'get_user_by_telegram_id(telegram_id={telegram_id})')
            async with DBSession() as session:
                # Формуємо запит
                query = select(User).filter_by(telegram_id=telegram_id)
                result = await session.execute(query)
                user = result.scalar()
                return user
        except Exception as e:
            logger.error(f"attempt={n + 1} error: {e}")
    return None


async def get_user_by_id(user_id: int) -> Optional[User]:
    """ Get User from DataBase by user_id """
    for n in range(3):
        try:
            logger.debug(f'get_user_by_id(user_id={user_id})')
            async with DBSession() as session:
                # Формуємо запит
                query = select(User).filter_by(id=user_id)
                result = await session.execute(query)
                user = result.scalar()
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


async def get_chat_with_user(pk: int = None, chat_id: int = None) -> Optional[Chat]:
    """ Get Chat by pk (primary key) and chat_id (id group in telegram) with the associated user """
    if not pk and not chat_id:
        return None
    for n in range(3):
        try:
            logger.debug(f'get_chat_with_user(pk={pk}, chat_id={chat_id})')
            async with DBSession() as session:
                # Створюємо запит
                query = select(Chat).options(selectinload(Chat.user))
                # Якщо обидва параметри передані, перевіряємо їх одночасно
                if pk and chat_id:
                    query = query.filter_by(id=pk, chat_id=chat_id)
                elif pk:
                    query = query.filter_by(id=pk)
                elif chat_id:
                    query = query.filter_by(chat_id=chat_id)
                result = await session.execute(query)
                chat = result.scalar()
                return chat
        except Exception as e:
            logger.error(f"attempt={n + 1} error: {e}")
    return None


async def get_chats(user_id: int = None, limit: int = None) -> List[Chat]:
    """ Get array with object<SQLAlchemy>: 'Chat' by optional user_id and optional limit """
    for n in range(3):
        try:
            logger.debug(f'get_chats(user_id={user_id}, limit={limit})')
            async with DBSession() as session:
                # Формуємо запит
                query = select(Chat)
                # Якщо передано user_id, додаємо фільтрацію
                if user_id:
                    query = query.filter_by(user_id=user_id)
                # Додаємо ліміт, якщо він переданий
                if limit:
                    query = query.limit(limit)
                result = await session.execute(query)
                chats = result.scalars().all()  # Отримуємо список чатів
                return chats
        except Exception as e:
            logger.error(f'Attempt {n + 1} failed: {e}')
    return []


def convert_str_to_datetime_fields(data: dict) -> dict:
    """Перетворює строки, які можуть бути датами, на об'єкти datetime."""
    for key, value in data.items():
        if isinstance(value, str):
            try:
                # Пробуємо перетворити строку на datetime
                data[key] = datetime.fromisoformat(value)
            except ValueError:
                # Якщо не вдалося, залишаємо строкове значення
                pass
    return data


async def create_new_doc(model: str, data: dict, data_has_datatime: bool = False) -> Optional[int]:
    """ Створюємо новий документ в базі даних, конвертуючи дати зі строк """
    if model in models:
        for n in range(3):
            try:
                logger.debug(f"model_name: {model}")
                if data_has_datatime:
                    # Конвертуємо строки у datetime, якщо це необхідно
                    data = convert_str_to_datetime_fields(data)
                async with DBSession() as session:
                    async with session.begin():
                        new_doc = models[model](**data)
                        session.add(new_doc)
                        await session.commit()
                        logger.info(f"created_new_doc(table={model}): new_doc.id={new_doc.id}")
                        return new_doc.id
            except Exception as e:
                logger.error(f"Attempt {n + 1}: Failed to create document='new_{model}' due to: {e}")
    else:
        logger.error(f"Invalid model name provided: {model}")
    return


import asyncio


async def test():
    chat = await get_chat_with_user(chat_id=-4546525808)
    print(chat.user.telegram_id)

# asyncio.run(test())