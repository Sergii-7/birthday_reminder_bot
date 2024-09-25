from datetime import datetime
from fastapi import Request, status, HTTPException, Form, APIRouter, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from create_app import app, limiter, templates
from config import bot_link
from src.sql.func_db import get_user_by_login, doc_update
from src.service.service_tools import correct_time
from src.service.loggers.py_logger_fast_api import get_logger

logger = get_logger(__name__)

user_router = APIRouter(prefix="/path", tags=["WIDGET-APP"])


@user_router.get(
    path="/login/{telegram_id}/{password}",
    include_in_schema=True,
    summary="Login user and set authentication cookies",
    status_code=status.HTTP_302_FOUND,
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
    '''
    https://holiday-organizer-dp6b4.ondigitalocean.app/path/login/620527199/XDXWYINdEh3ZkniDSX52T9aj53j
    '''
    ip_address, page = dict(request.headers).get('x-forwarded-for'), 'login'
    logger.info(f"time_now: {correct_time()}, /{page}/telegram_id={telegram_id}, ip_address={ip_address}")
    # Перевірка користувача
    user = await get_user_by_login(telegram_id=telegram_id, password=password)
    if user:
        # Використання заголовків для встановлення кукі
        response = RedirectResponse(url="/path/birthday", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="telegram_id", value=str(telegram_id), path="/", samesite="Lax", secure=True)
        response.set_cookie(key="user_password", value=password, path="/", samesite="Lax", secure=True)
        return response
    else:
        # Якщо дані невірні
        msg = "Data is not valid!"
        logger.error(msg=msg)
        detail = [{"success": False, "msg": msg}]
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


@user_router.get(
    path="/birthday", include_in_schema=True, response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def set_birthday(request: Request):
    """
    Checks if the user is authenticated by verifying cookies.
    """
    ip_address, page = dict(request.headers).get('x-forwarded-for'), 'birthday'
    telegram_id, password = request.cookies.get("telegram_id"), request.cookies.get("user_password")
    logger.info(f"time_now: {correct_time()}, /{page} telegram_id={telegram_id}, ip_address={ip_address}")
    # Перевірка користувача в базі даних
    user_login = await get_user_by_login(
        telegram_id=int(telegram_id), password=password) if telegram_id and password else None
    if user_login:
        data = {'title': ' Аврора', 'msg': 'Обери дату свого народження:'}
        return templates.TemplateResponse("birthday.html", {"request": request, "data": data})
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


@user_router.post(
    path='/get_birthday', include_in_schema=True, status_code=status.HTTP_302_FOUND)
async def get_birthday(request: Request, birthday: str = Form(...)):
    """

    :param request:
    :return:
    """
    ip_address, page = dict(request.headers).get('x-forwarded-for'), 'get_birthday'
    telegram_id, password = request.cookies.get("telegram_id"), request.cookies.get("user_password")
    logger.info(f"time_now: {correct_time()}, /{page} telegram_id={telegram_id}, ip_address={ip_address}")
    # Перевірка користувача в базі даних
    user_login = await get_user_by_login(
        telegram_id=int(telegram_id), password=password) if telegram_id and password else None
    if user_login:
        user_login.user.birthday = datetime.strptime(birthday, "%Y-%m-%d") if birthday else None
        ''' Update User in DataBase '''
        user_login = await doc_update(doc=user_login)
        res = "User.birthday updated successfully!" if user_login else "Error in updating User.birthday!"
        logger.info(res)
        response = RedirectResponse(url=bot_link, status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="telegram_id", value=str(telegram_id), path="/", samesite="Lax", secure=True)
        response.set_cookie(key="user_password", value=password, path="/", samesite="Lax", secure=True)
        return response
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


# Підключення маршрутів 'USER' до основного додатку
app.include_router(router=user_router)