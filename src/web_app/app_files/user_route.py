from fastapi import Request, status, HTTPException, Body, APIRouter
from fastapi.responses import JSONResponse, HTMLResponse
from create_app import app, limiter, templates
from src.sql import func_db
from src.service.service_tools import correct_time
from src.service.loggers.py_logger_fast_api import get_logger

logger = get_logger(__name__)

user_router = APIRouter(prefix="/path", tags=["WIDGET-APP"])


@user_router.get(path="/login/{telegram_id}/{password}", include_in_schema=True, status_code=status.HTTP_200_OK)
@limiter.limit("60/minute")
async def login(request: Request, telegram_id: int, password: str):
    """

    **Args:**
    - telegram_id (int)
    - password (str): Password must contain only Latin letters and/or digits.

    **Returns:**
    - 200: If success, returns  ___???___ .
    - 422: If validation error, returns an object with error message.
    """
    ip_address, page = dict(request.headers).get('x-forwarded-for'), 'login'
    logger.info(f"time_now: {correct_time()}, /{page}/telegram_id={telegram_id}, ip_address={ip_address}")
    user = await func_db.get_user_by_login(telegram_id=telegram_id, password=password)
    if user:
        """ Треба зашити в браузер (в Хедерс чи в кукі) параметри для індифікації користувача,
        а саме telegram_id та password 
        та зробити редірект на іншу сторінку """
        ...
    else:
        msg = "Data is not valid!"
        logger.error(msg=msg)
        detail = [{"success": False, "msg": msg}]
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

# Підключення маршрутів 'USER' до основного додатку
app.include_router(router=user_router)