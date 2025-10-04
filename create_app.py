from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from config import HOST, STATIC_FILES, TEMPLATES

security = HTTPBasic()

app = FastAPI(debug=False, docs_url=None, redoc_url=None, openapi_url=None)

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

# Ініціалізація лімітера
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
