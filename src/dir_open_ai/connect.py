from openai import AsyncOpenAI

from config import API_KEY_OPENAI
from src.service.loggers.py_logger_openai import get_logger

logger = get_logger(__name__)
logger.debug("connect with openai")

client = AsyncOpenAI(api_key=API_KEY_OPENAI)
