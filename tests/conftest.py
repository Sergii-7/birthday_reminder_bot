"""
Конфігурація pytest для всіх тестів.
Включає заглушки для баз даних і основних залежностей.
"""

import asyncio
import os
import sys
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Додаємо src до Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# Налаштування asyncio для тестів
@pytest.fixture(scope="session")
def event_loop():
    """Створює event loop для всієї сесії тестування."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# === ЗАГЛУШКИ ДЛЯ ЗОВНІШНІХ ЗАЛЕЖНОСТЕЙ ===


@pytest.fixture(scope="session", autouse=True)
def mock_external_libraries():
    """Автоматичне мокування зовнішніх бібліотек."""
    with patch.dict(
        "sys.modules",
        {
            "aiogram": MagicMock(),
            "aiogram.types": MagicMock(),
            "aiogram.dispatcher": MagicMock(),
            "aiogram.filters": MagicMock(),
            "aiogram.fsm": MagicMock(),
            "aiogram.fsm.context": MagicMock(),
            "aiogram.fsm.state": MagicMock(),
            "openai": MagicMock(),
            "motor": MagicMock(),
            "motor.motor_asyncio": MagicMock(),
            "redis": MagicMock(),
            "redis.asyncio": MagicMock(),
            "fastapi_limiter": MagicMock(),
            "PIL": MagicMock(),
            "PIL.Image": MagicMock(),
        },
    ):
        yield


# === ЗАГЛУШКИ ДЛЯ БАЗ ДАНИХ ===


@pytest.fixture
def mock_db_session():
    """Заглушка для SQL сесії бази даних."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    session.scalars = AsyncMock()
    return session


@pytest.fixture
def mock_mongo_client():
    """Заглушка для MongoDB клієнта."""
    client = MagicMock()
    db = MagicMock()
    collection = MagicMock()

    client.__getitem__.return_value = db
    db.__getitem__.return_value = collection

    # Async methods
    collection.find_one = AsyncMock()
    collection.insert_one = AsyncMock()
    collection.update_one = AsyncMock()
    collection.delete_one = AsyncMock()
    collection.find = MagicMock()

    return client


@pytest.fixture
def mock_redis_client():
    """Заглушка для Redis клієнта."""
    client = AsyncMock()
    client.ping = AsyncMock(return_value=True)
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock(return_value=True)
    client.delete = AsyncMock(return_value=1)
    client.close = AsyncMock()
    return client


# === ЗАГЛУШКИ ДЛЯ TELEGRAM BOT ===


@pytest.fixture
def mock_telegram_bot():
    """Заглушка для Telegram Bot."""
    bot = AsyncMock()
    bot.send_message = AsyncMock()
    bot.send_photo = AsyncMock()
    bot.send_document = AsyncMock()
    bot.edit_message_text = AsyncMock()
    bot.answer_callback_query = AsyncMock()
    return bot


@pytest.fixture
def mock_telegram_message():
    """Заглушка для Telegram Message."""
    message = MagicMock()
    message.message_id = 123
    message.chat = MagicMock()
    message.chat.id = 456
    message.from_user = MagicMock()
    message.from_user.id = 789
    message.text = "Test message"
    message.answer = AsyncMock()
    message.reply = AsyncMock()
    return message


@pytest.fixture
def mock_telegram_callback():
    """Заглушка для Telegram CallbackQuery."""
    callback = MagicMock()
    callback.id = "callback_123"
    callback.data = "test_data"
    callback.message = MagicMock()
    callback.from_user = MagicMock()
    callback.from_user.id = 789
    callback.answer = AsyncMock()
    return callback


# === ЗАГЛУШКИ ДЛЯ OPENAI ===


@pytest.fixture
def mock_openai_client():
    """Заглушка для OpenAI клієнта."""
    client = MagicMock()

    # Chat completions
    client.chat = MagicMock()
    client.chat.completions = MagicMock()
    client.chat.completions.create = AsyncMock()

    # Images
    client.images = MagicMock()
    client.images.generate = AsyncMock()
    client.images.create_variation = AsyncMock()

    return client


# === ЗАГЛУШКИ ДЛЯ КОНФІГУРАЦІЇ ===


@pytest.fixture(autouse=True)
def mock_config():
    """Мокування конфігураційних змінних."""
    # Створюємо мок модуль config
    config_mock = MagicMock()
    config_mock.URI_DB = "sqlite:///:memory:"
    config_mock.MONGO_URI = "mongodb://localhost:27017/test"
    config_mock.API_KEY_OPENAI = "test_openai_key"
    config_mock.TOKEN = "test_telegram_token"
    config_mock.REDIS_HOST = "localhost"
    config_mock.REDIS_PORT = 6379

    with patch.dict("sys.modules", {"config": config_mock}):
        yield


# === ЛОГУВАННЯ ===


@pytest.fixture(autouse=True)
def mock_loggers():
    """Мокування всіх логерів."""
    # Створюємо мок логер
    logger_instance = MagicMock()
    logger_instance.info = MagicMock()
    logger_instance.error = MagicMock()
    logger_instance.warning = MagicMock()
    logger_instance.debug = MagicMock()

    # Створюємо мок модулі логерів
    logger_modules = {}
    logger_names = [
        "src.service.loggers.py_logger_sql",
        "src.service.loggers.py_logger_fast_api",
        "src.service.loggers.py_logger_tel_bot",
        "src.service.loggers.py_logger_openai",
    ]

    for module_name in logger_names:
        mock_module = MagicMock()
        mock_module.get_logger = MagicMock(return_value=logger_instance)
        logger_modules[module_name] = mock_module

    with patch.dict("sys.modules", logger_modules):
        yield
