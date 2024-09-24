from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.token import TokenValidationError
from aiogram.client.bot import DefaultBotProperties
from config import TOKEN
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)

try:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
except TokenValidationError:
    logger.error("Invalid Token provided!")
    raise ValueError("Invalid Token provided!")

dp = Dispatcher(storage=MemoryStorage())