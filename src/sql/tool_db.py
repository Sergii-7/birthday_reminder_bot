import asyncio
from functools import wraps

from sqlalchemy.exc import OperationalError, SQLAlchemyError

from src.service.loggers.py_logger_sql import get_logger

logger = get_logger(__name__)


def retry_on_db_error(max_retries: int = 3, delay: float = 0.5):
    """Декоратор для повтору асинхронних запитів до БД при помилках підключення."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    logger.debug(msg=f"Executing {func.__name__} (attempt {attempt + 1})")
                    return await func(*args, **kwargs)  # Виконуємо асинхронну функцію
                except OperationalError as e:
                    logger.error(msg=f"Database connection error on attempt {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)  # Асинхронна затримка перед повтором
                except SQLAlchemyError as e:
                    logger.error(msg=f"SQLAlchemy error in {func.__name__}: {e}")
                    break  # Інші помилки SQLAlchemy не повторюємо
                except Exception as e:
                    logger.error(msg=f"Unexpected error in {func.__name__}: {e}")
                    break
            return None  # Якщо всі спроби не вдалися

        return wrapper

    return decorator
