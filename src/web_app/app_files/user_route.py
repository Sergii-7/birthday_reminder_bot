from fastapi import Request, status, HTTPException, Body, APIRouter, Response, Depends
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from typing import Union
from create_app import app, limiter, templates
from src.sql.func_db import get_user_by_login
from src.sql.models import User, UserLogin
from src.web_app.app_files.app_access import get_current_user
from src.service.service_tools import correct_time
from src.service.loggers.py_logger_fast_api import get_logger

logger = get_logger(__name__)

user_router = APIRouter(prefix="/path", tags=["WIDGET-APP"])


@user_router.get(
    path="/login/{telegram_id}/{password}",
    include_in_schema=True,
    summary="Login user and set authentication cookies",
    description="""
        Logs in the user with the provided `telegram_id` and `password`. 
        If the credentials are correct, sets cookies for user identification and redirects to another page.

        **Args:**
        - `telegram_id` (int): User's Telegram ID.
        - `password` (str): Password containing only Latin letters and/or digits.

        **Returns:**
        - `302`: On success, sets cookies for `telegram_id` and `password`, then redirects the user.
        - `422`: If validation error occurs, returns an object with an error message.

        **Note:**
        - Cookies are used to store `telegram_id` and `password` for further requests, allowing the user to remain logged in.
        - Cookies are not hashed, so storing sensitive information like passwords should be handled carefully.
    """
)
@limiter.limit("60/minute")
async def login(request: Request, response: Response, telegram_id: int, password: str):
    """
    Handles user login and sets cookies with authentication data.

    - The user remains logged in by storing `telegram_id` and `password` in cookies.
    - Redirects to a specific page after successful login.
    """
    ip_address, page = dict(request.headers).get('x-forwarded-for'), 'login'
    logger.info(f"time_now: {correct_time()}, /{page}/telegram_id={telegram_id}, ip_address={ip_address}")
    # Перевірка користувача
    user = await get_user_by_login(telegram_id=telegram_id, password=password)
    if user:
        # Збереження ідентифікаційних даних користувача у кукі з розширеними параметрами
        response.set_cookie(
            key="telegram_id", value=str(telegram_id), httponly=True, path="/", samesite="Lax", secure=True)
        response.set_cookie(
            key="password", value=password, httponly=True, path="/", samesite="Lax", secure=True)
        # Переадресація на іншу сторінку після успішного входу
        return RedirectResponse(url="/path/another_page", status_code=status.HTTP_302_FOUND)
    else:
        # Якщо дані невірні
        msg = "Data is not valid!"
        logger.error(msg=msg)
        detail = [{"success": False, "msg": msg}]
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


@user_router.get(path="/another_page", include_in_schema=True, status_code=status.HTTP_200_OK)
async def check_auth(request: Request):
    """
    Checks if the user is authenticated by verifying cookies.
    """
    # https://holiday-organizer-dp6b4.ondigitalocean.app/path/login/620527199/XDXWYINdEh3ZkniDSX52T9aj53j
    telegram_id = request.cookies.get("telegram_id")
    logger.info(f"telegram_id={telegram_id}")
    password = request.cookies.get("password")
    logger.info(f"password={password}")
    # Перевірка користувача в базі даних
    if telegram_id:
        return JSONResponse({"success": True, "message": "User is authenticated."})
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

# Підключення маршрутів 'USER' до основного додатку
app.include_router(router=user_router)