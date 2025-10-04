from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.token import TokenValidationError

# from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN
from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)

try:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
except TokenValidationError:
    msg = "Invalid Token provided!"
    logger.error(msg=msg)
    raise ValueError(msg)

# dp = Dispatcher(storage=MemoryStorage())
dp = Dispatcher()
