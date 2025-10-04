import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_limiter import FastAPILimiter

from config import HOST, REDIS_HOST, REDIS_NUMBER_DB, REDIS_PORT, REDIS_TIMEOUT, STATIC_FILES, TEMPLATES
from src.service.loggers.py_logger_fast_api import get_logger

logger = get_logger(__name__)

security = HTTPBasic()

app = FastAPI(debug=False, docs_url=None, redoc_url=None, openapi_url=None)


redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_NUMBER_DB,
    socket_timeout=REDIS_TIMEOUT,
)


async def check_redis_connection():
    try:
        await redis_client.ping()
        logger.info(msg="Підключення до Redis успішне.")
    except Exception as e:
        logger.error(msg=f"Помилка підключення до Redis: {e}")
        raise RuntimeError("Не вдалося підключитися до Redis.")


@app.on_event(event_type="startup")
async def startup():
    await check_redis_connection()
    await FastAPILimiter.init(redis=redis_client)


@app.on_event(event_type="shutdown")
async def shutdown():
    await redis_client.close()


# Обслуговування статичних файлів (CSS, зображення, JS)
app.mount(path="/static", app=StaticFiles(directory=STATIC_FILES), name="static")

# Ініціалізація шаблонів Jinja2
templates = Jinja2Templates(directory=TEMPLATES)


# Додаємо middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        HOST,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
