from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


security = HTTPBasic()

app = FastAPI(debug=False, docs_url=None, redoc_url=None, openapi_url=None)

# Обслуговування статичних файлів (CSS, зображення, JS)
app.mount(path="/static", app=StaticFiles(directory="src/web_app/static"), name="static")

# Ініціалізація шаблонів Jinja2
templates = Jinja2Templates(directory="src/web_app/templates")


# Додаємо middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Змініть це на список URL вашого клієнта
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ініціалізація лімітера
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
