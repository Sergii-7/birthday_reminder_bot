import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Додаємо src до Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def mock_external_libraries():
    # Детальне мокування aiogram
    aiogram_mock = MagicMock()
    aiogram_types_mock = MagicMock()
    aiogram_enums_mock = MagicMock()
    aiogram_client_mock = MagicMock()

    # Мокуємо основні класи aiogram
    aiogram_mock.Bot = MagicMock()
    aiogram_mock.Dispatcher = MagicMock()
    aiogram_types_mock.Message = MagicMock()
    aiogram_types_mock.CallbackQuery = MagicMock()
    aiogram_types_mock.InlineKeyboardMarkup = MagicMock()
    aiogram_types_mock.InlineKeyboardButton = MagicMock()
    aiogram_enums_mock.ParseMode = MagicMock()
    aiogram_client_mock.bot = MagicMock()
    aiogram_client_mock.bot.DefaultBotProperties = MagicMock()

    with patch.dict(
        "sys.modules",
        {
            "aiogram": aiogram_mock,
            "aiogram.types": aiogram_types_mock,
            "aiogram.enums": aiogram_enums_mock,
            "aiogram.client": aiogram_client_mock,
            "aiogram.client.bot": aiogram_client_mock.bot,
            "aiogram.dispatcher": MagicMock(),
            "aiogram.filters": MagicMock(),
            "aiogram.fsm": MagicMock(),
            "aiogram.fsm.context": MagicMock(),
            "aiogram.fsm.state": MagicMock(),
            "aiogram.utils": MagicMock(),
            "aiogram.utils.token": MagicMock(),
            "openai": MagicMock(),
            "openai.types": MagicMock(),
            "openai.types.chat": MagicMock(),
            "motor": MagicMock(),
            "motor.motor_asyncio": MagicMock(),
            "redis": MagicMock(),
            "PIL": MagicMock(),
            # Mock source modules to prevent AttributeError
            "src.bot_app.create_bot": MagicMock(),
            "src.bot_app.command": MagicMock(),
            "src.bot_app.message": MagicMock(),
            "src.bot_app.callback": MagicMock(),
            "src.web_app.create_app": MagicMock(),
            "src.bot_app.dir_menu.buttons_for_menu": MagicMock(),
        },
    ):

        # Set up specific AsyncMock functions that are commonly tested
        import sys

        if "src.bot_app.callback" in sys.modules:
            sys.modules["src.bot_app.callback"].callback_handler = AsyncMock()
        if "src.bot_app.command" in sys.modules:
            sys.modules["src.bot_app.command"].start_command_admin = AsyncMock()
            sys.modules["src.bot_app.command"].help_command = AsyncMock()
        if "src.bot_app.message" in sys.modules:
            sys.modules["src.bot_app.message"].text_handler = AsyncMock()
            sys.modules["src.bot_app.message"].photo_handler = AsyncMock()
            sys.modules["src.bot_app.message"].document_handler = AsyncMock()
            sys.modules["src.bot_app.message"].birthday_input_handler = AsyncMock()
        if "src.web_app.create_app" in sys.modules:
            sys.modules["src.web_app.create_app"].check_redis_connection = AsyncMock()
            sys.modules["src.web_app.create_app"].startup = AsyncMock()
            sys.modules["src.web_app.create_app"].shutdown = AsyncMock()
        if "src.bot_app.dir_menu.buttons_for_menu" in sys.modules:
            # Set up return values for button menu functions
            sys.modules["src.bot_app.dir_menu.buttons_for_menu"].generate_callback_data = MagicMock(
                return_value="menu:main:action"
            )
            sys.modules["src.bot_app.dir_menu.buttons_for_menu"].get_button_text = MagicMock(return_value="Button Text")
            sys.modules["src.bot_app.dir_menu.buttons_for_menu"].organize_buttons_in_rows = MagicMock(
                return_value=[["button1", "button2"]]
            )

        # Setup common database function mocks with realistic return values
        if "src.sql.func_db" in sys.modules:
            mock_user = MagicMock()
            mock_user.user_id = 123456
            mock_user.username = "test_user"
            sys.modules["src.sql.func_db"].get_user_by_id = AsyncMock(return_value=mock_user)
            sys.modules["src.sql.func_db"].create_user = AsyncMock(return_value=mock_user)
            sys.modules["src.sql.func_db"].update_user = AsyncMock(return_value=True)

        yield


@pytest.fixture(autouse=True)
def mock_config():
    config_mock = MagicMock()
    config_mock.URI_DB = "user:pass@localhost:5432/testdb"  # Правильний формат PostgreSQL URL
    config_mock.MONGO_URI = "mongodb://localhost:27017/test"
    config_mock.API_KEY_OPENAI = "test_openai_key"
    config_mock.TOKEN = "test_telegram_token"
    config_mock.REDIS_HOST = "localhost"
    config_mock.REDIS_PORT = 6379

    # Додатково мокуємо як змінні середовища
    with (
        patch.dict("sys.modules", {"config": config_mock}),
        patch.dict(
            os.environ,
            {
                "URI_DB": "user:pass@localhost:5432/testdb",
                "MONGO_URI": "mongodb://localhost:27017/test",
                "API_KEY_OPENAI": "test_openai_key",
                "TOKEN": "test_telegram_token",
                "REDIS_HOST": "localhost",
                "REDIS_PORT": "6379",
            },
        ),
    ):
        yield


@pytest.fixture(autouse=True)
def mock_loggers():
    logger_instance = MagicMock()
    logger_modules = {
        "src.service.loggers.py_logger_sql": MagicMock(),
        "src.service.loggers.py_logger_fast_api": MagicMock(),
        "src.service.loggers.py_logger_tel_bot": MagicMock(),
        "src.service.loggers.py_logger_openai": MagicMock(),
    }
    for module in logger_modules.values():
        module.get_logger = MagicMock(return_value=logger_instance)

    with patch.dict("sys.modules", logger_modules):
        # Додатково мокуємо SQLAlchemy модулі для безпечного імпорту
        with (
            patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=MagicMock()),
            patch("sqlalchemy.ext.asyncio.AsyncSession", MagicMock()),
            patch("sqlalchemy.create_engine", return_value=MagicMock()),
            patch("src.sql.connect.create_async_engine", return_value=MagicMock()),
            patch("src.sql.connect.DBSession", MagicMock()),
        ):
            yield


@pytest.fixture
def mock_bot():
    bot = AsyncMock()
    bot.send_message = AsyncMock()
    bot.send_photo = AsyncMock()
    bot.send_document = AsyncMock()
    return bot


@pytest.fixture
def mock_message():
    message = MagicMock()
    message.from_user = MagicMock()
    message.from_user.id = 123456
    message.chat = MagicMock()
    message.chat.id = 123456
    message.answer = AsyncMock()
    message.edit_text = AsyncMock()
    return message


@pytest.fixture
def mock_callback():
    callback = MagicMock()
    callback.from_user = MagicMock()
    callback.from_user.id = 123456
    callback.message = MagicMock()
    callback.message.chat = MagicMock()
    callback.message.chat.id = 123456
    callback.answer = AsyncMock()
    callback.message.edit_text = AsyncMock()
    return callback


@pytest.fixture
def mock_message_data():
    return {"chat_id": 123456, "user_id": 789012, "text": "Test message", "timestamp": "2024-01-01 12:00:00"}


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


@pytest.fixture
def mock_db_session():
    """Заглушка для сесії бази даних."""
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    session.get = AsyncMock()
    session.query = MagicMock()
    return session


@pytest.fixture
def mock_logger():
    """Заглушка для логгера."""
    logger = MagicMock()
    logger.info = MagicMock()
    logger.error = MagicMock()
    logger.warning = MagicMock()
    logger.debug = MagicMock()
    return logger


@pytest.fixture
def mock_telegram_bot():
    """Заглушка для Telegram бота."""
    bot = MagicMock()
    bot.send_message = AsyncMock()
    bot.send_photo = AsyncMock()
    bot.send_document = AsyncMock()
    bot.edit_message_text = AsyncMock()
    bot.answer_callback_query = AsyncMock()
    return bot


@pytest.fixture
def mock_mongo_client():
    """Заглушка для MongoDB клієнта."""
    client = MagicMock()
    client.get_database = MagicMock()
    client.close = AsyncMock()
    return client


@pytest.fixture
def mock_redis_client():
    """Заглушка для Redis клієнта."""
    redis = MagicMock()
    redis.get = AsyncMock()
    redis.set = AsyncMock()
    redis.delete = AsyncMock()
    redis.ping = AsyncMock(return_value=True)
    redis.close = AsyncMock()
    return redis
