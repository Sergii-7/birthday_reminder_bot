from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_limiter import FastAPILimiter

from config import HOST, REDIS_HOST, REDIS_NUMBER_DB, REDIS_PORT, REDIS_TIMEOUT, STATIC_FILES, TEMPLATES
from src.service.loggers.py_logger_fast_api import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_NUMBER_DB}"
    redis_client = redis.from_url(
        redis_url,
        encoding="utf-8",
        decode_responses=True,
        socket_timeout=REDIS_TIMEOUT,  # таймаут операцій
        socket_connect_timeout=5,  # таймаут встановлення з'єднання
        health_check_interval=30,  # періодичний ping у бекграунді
        max_connections=100,  # пул конекшенів
    )

    try:
        await redis_client.ping()
        logger.info("Підключення до Redis успішне.")
        await FastAPILimiter.init(redis=redis_client)
        # збережемо клієнт у state, щоб закрити у shutdown
        app.state.redis_client = redis_client
    except Exception as e:
        logger.exception(f"Помилка підключення до Redis: {e}")
        # важливо закрити пул, якщо частково ініціалізувався
        try:
            await redis_client.close()
            await redis_client.connection_pool.disconnect()
        except Exception:
            pass
        raise

    yield

    # --- shutdown ---
    try:
        client = app.state.redis_client
        await client.close()
        # додатково гарантуємо закриття всіх з'єднань
        await client.connection_pool.disconnect()
    except Exception as e:
        logger.warning(f"Помилка під час закриття Redis: {e}")


app = FastAPI(
    debug=False,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)

# Статика та шаблони
app.mount(path="/static", app=StaticFiles(directory=STATIC_FILES), name="static")
templates = Jinja2Templates(directory=TEMPLATES)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[HOST],  # або ["*"] якщо потрібно тестувати з локалхоста
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
