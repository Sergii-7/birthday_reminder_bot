from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
import secrets
from config import ADMIN_LOGIN, ADMIN_PASSWORD


security = HTTPBasic()

app = FastAPI(debug=False, docs_url=None, redoc_url=None, openapi_url=None)

# Обслуговування статичних файлів (CSS, зображення, JS)
app.mount(path="/static", app=StaticFiles(directory="app_files/static"), name="static")

# Ініціалізація шаблонів Jinja2
templates = Jinja2Templates(directory="app_files/templates")


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, ADMIN_LOGIN)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


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
