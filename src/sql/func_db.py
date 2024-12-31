from asyncio import sleep
from datetime import datetime
from typing import Optional, Union, List, Dict, Any
from aiogram.types import Message
from sqlalchemy import and_
from sqlalchemy.future import select
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import joinedload, selectinload, SQLORMExpression

from src.sql.connect import DBSession
from src.sql.models import User, UserLogin, UserChat, Chat, Holiday, Report
from src.service.service_tools import correct_time
from src.service.loggers.py_logger_fast_api import get_logger

logger = get_logger(__name__)

models = {
    'user': User, 'user_login': UserLogin, 'user_chat': UserChat, 'chat': Chat, 'holiday': Holiday, 'report': Report,
}


async def get_doc_by_id(model: str, doc_id: int) -> Optional[Union[User, UserLogin, UserChat, Chat, Holiday, Report]]:
    """ Get doc from DataBase by id """
    if model in models:
        for n in range(3):
            try:
                logger.debug(f"get_doc_by_id(model={model}, doc_id={doc_id})")
                async with DBSession() as session:
                    query = select(models[model]).filter_by(id=doc_id)
                    result = await session.execute(query)
                    doc = result.scalar()
                    return doc
            except Exception as e:
                logger.error(f"Attempt {n+1}: {e}")
                await sleep(0.5)
    else:
        logger.error(f"Invalid model name provided: {model}")
    return None


async def check_user(message: Message) -> Optional[User]:
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
            await sleep(0.5)
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
            await sleep(0.5)
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
            await sleep(0.5)
    return None


async def get_user_by_phone(phone_number: str) -> Optional[User]:
    """ Get User from DataBase by phone_number """
    for n in range(3):
        try:
            logger.debug(f'get_user_by_phone(phone_number={phone_number})')
            async with DBSession() as session:
                # Формуємо запит
                query = select(User).filter_by(phone_number=phone_number)
                result = await session.execute(query)
                user = result.scalar()
                return user
        except Exception as e:
            logger.error(f"attempt={n + 1} error: {e}")
            await sleep(0.5)
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
            await sleep(0.5)
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
            await sleep(0.5)
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
            await sleep(0.5)
    return None


async def doc_update(
        doc: Union[User, UserLogin, UserChat, Chat, Holiday, Report]
) -> Union[bool, Union[User, UserLogin, UserChat, Chat, Holiday, Report]]:
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
                await sleep(0.5)
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
                # Якщо обидва параметри передані, передаємо їх одночасно
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
            await sleep(0.5)
    return None


async def get_user_chat_with_user(user_chat_pk: int) -> Optional[UserChat]:
    """ Get UserChat with User """
    for n in range(3):
        try:
            logger.debug(f"get_user_chat_with_user(user_chat_pk={user_chat_pk})")
            async with DBSession() as session:
                stmt = (
                    select(UserChat)
                    .options(selectinload(UserChat.user))  # Завантажуємо пов'язаний об'єкт User
                    .filter(UserChat.id == user_chat_pk)
                )
                result = await session.execute(stmt)
                return result.scalars().first()
        except Exception as e:
            logger.error(f"Attempt={n+1}: {e}")
            await sleep(0.5)
    return None


async def get_users(filter_by_birthday: bool = False) -> List[User]:
    """ Get all users from DataBase, optionally filter by non-null birthday """
    for n in range(3):
        try:
            logger.debug("get_all_users()")
            async with DBSession() as session:
                query = select(User)
                # Додаємо фільтр, якщо це необхідно
                if filter_by_birthday:
                    query = query.where(User.birthday.isnot(None))
                result = await session.execute(query)
                users = result.scalars().all()  # Отримуємо список users
                return users
        except Exception as e:
            logger.error(f"Attempt={n + 1}: {e}")
            await sleep(0.5)
    return []


async def get_chats(user_id: int = None, status: bool = None, limit: int = None) -> List[Chat]:
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
                # Якщо передано status, додаємо фільтрацію
                if status is not None:
                    query = query.filter_by(status=status)
                # Додаємо ліміт, якщо він переданий
                if limit:
                    query = query.limit(limit)
                result = await session.execute(query)
                chats = result.scalars().all()  # Отримуємо список чатів
                return chats
        except Exception as e:
            logger.error(f'Attempt {n + 1} failed: {e}')
            await sleep(0.5)
    return []


async def get_user_chat(chat_id: int, user_telegram_id: int) -> Optional[UserChat]:
    """ Get UserChat from DataBase by 'chat.id' and 'user.telegram_id' """
    for n in range(3):
        try:
            logger.debug(f"get_user_chat(chat_id={chat_id}, user_telegram_id={user_telegram_id})")
            async with DBSession() as session:
                query = select(UserChat).filter(
                    and_(
                        UserChat.chat_id == chat_id,
                        UserChat.user_telegram_id == user_telegram_id
                    )
                )
                result = await session.execute(query)
                return result.scalar_one_or_none()
        except Exception as err:
            logger.error(f"attempt={n+1}: {err}")
            await sleep(0.5)
    return None


async def get_all_users_from_chat(chat_id: int) -> List[UserChat]:
    """ Get all users from UserChat by 'chat.id' with associated User """
    for n in range(3):
        try:
            logger.debug(f"get_all_users_from_chat(chat_id={chat_id})")
            async with DBSession() as session:
                query = select(UserChat).options(joinedload(UserChat.user)).filter_by(chat_id=chat_id)
                result = await session.execute(query)
                return result.scalars().all()
        except Exception as err:
            logger.error(f"attempt={n+1}: {err}")
            await sleep(0.5)
    return []


async def get_holiday_with_chat(holiday_id: int) -> Optional[Holiday]:
    """ Get Holiday by id (primary key) with the associated chat """
    for n in range(3):
        try:
            logger.debug(f'get_holiday_with_chat(holiday_id={holiday_id})')
            async with DBSession() as session:
                # Створюємо запит
                query = select(Holiday).options(selectinload(Holiday.chat))
                # Якщо обидва параметри передані, перевіряємо їх одночасно
                query = query.filter_by(id=holiday_id)
                result = await session.execute(query)
                holiday = result.scalar()
                return holiday
        except Exception as e:
            logger.error(f"attempt={n + 1} error: {e}")
            await sleep(0.5)
    return None


async def get_holiday(user_pk: int, chat_pk: int):
    """Get Holiday by user_pk (ForeignKey) and chat_pk (ForeignKey)"""
    for n in range(3):
        try:
            logger.debug(f'get_holiday(user_pk={user_pk}, chat_pk={chat_pk})')
            async with DBSession() as session:
                query = select(Holiday).where(and_(Holiday.user_id == user_pk, Holiday.chat_id == chat_pk))
                result = await session.execute(query)
                holiday = result.scalar()
                return holiday
        except Exception as e:
            logger.error(f"attempt={n + 1} error: {e}")
            await sleep(0.5)
    return None


async def get_report(user_pk: int, chat_pk: int, holiday_pk: int) -> Optional[Report]:
    """Find Report in DataBase and return it or return None if not found."""
    for n in range(3):
        try:
            logger.debug(f"get_report(user_pk={user_pk}, chat_pk={chat_pk}, holiday_pk={holiday_pk})")
            async with DBSession() as session:
                query = select(Report).where(
                    and_(
                        Report.user_id == user_pk,
                        Report.chat_id == chat_pk,
                        Report.holiday_id == holiday_pk
                    )
                )
                result = await session.execute(query)
                report = result.scalar_one_or_none()
                return report
        except Exception as e:
            logger.error(f"Attempt {n+1}: {e}")
            await sleep(0.5)  # Додаємо затримку перед повторною спробою
    return None


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


async def object_as_dict(obj: object) -> Dict[str, Any]:
    """ Перетворюємо object з DataBase на dict """
    if not hasattr(obj, '__table__'):
        raise ValueError(f"Expected SQLAlchemy model instance, got {obj.__class__}")
    result = {}
    for c in inspect(obj).mapper.column_attrs:
        value = getattr(obj, c.key)
        if isinstance(value, datetime):
            value = value.isoformat()  # Конвертуємо datetime в строку ISO 8601 формату
        elif isinstance(value, bool):
            value = value  # Залишаємо булінгове значення як є
        result[c.key] = value
    return result


async def get_all_docs(model: str) -> List[Union[User, UserLogin, UserChat, Chat, Holiday, Report]]:
    """Get all docs from PostgreSQL DataBase from table 'model'."""
    if model not in models:
        logger.error(f"model: {model} is invalid!")
        return []
    model: Union[User, UserLogin, UserChat, Chat, Holiday, Report] = models[model]
    try:
        logger.debug(f"get docs from {model.__tablename__}")
        async with DBSession() as session:
            query = select(model)
            result = await session.execute(query)
            docs = result.scalars().all()  # Отримуємо список docs
            return docs
    except SQLORMExpression as e:
        logger.error(msg=str(e))
    return []


async def get_user_reports(user_id: int, status: Optional[bool] = None) -> Optional[List[Report]]:
    """
    Отримати всі репорти для користувача за user_id.
    :param user_id: ID користувача для пошуку репортів.
    :param status: Фільтрація за статусом (True/False). Якщо None, статус не враховується.
    :return: Список об'єктів Report.
    """
    try:
        logger.debug(f"user_id={user_id}, status={status}")
        async with DBSession() as session:
            query = select(Report).options(
                joinedload(Report.chat),
                joinedload(Report.holidays),
            ).where(Report.user_id == user_id)
            if status is not None:
                query = query.where(Report.status == status)
            result = await session.execute(query)
            return result.scalars().all()
    except SQLORMExpression as e:
        logger.error(msg=e)
    return


# import asyncio
# from config import sb_telegram_id
#
# async def test():
#     user = await get_user_by_telegram_id(telegram_id=sb_telegram_id)
#     print(user.birthday)
#
# asyncio.run(test())