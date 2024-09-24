import asyncio
from fastapi import Request, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi import status, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from src.web_app.app_files.app_access import get_current_admin
from src.service.service_tools import correct_time
from create_app import app, limiter, templates
from src.sql.models import AdminApp
from src.bot_app.create_bot import bot
from config import file_log_fast_api, file_log_tel_bot
from config import sb_telegram_id
from src.service.loggers.py_logger_fast_api import get_logger

logger = get_logger(__name__)


@app.get(path="/", response_class=HTMLResponse, include_in_schema=False, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def home(request: Request, admin: AdminApp = Depends(get_current_admin)):
    """ Перевірка робота додатка """
    time_now = correct_time()
    headers = dict(request.headers)
    ip_address, page = headers.get('x-forwarded-for'), 'home'
    logger.info(f"{time_now}: {admin.login} in page '{page}'\nip_address: {ip_address}")
    data = {
        "title": "Аврора", "message": "Welcome to the 'Holiday organizer App' API !",
        "redoc": "see the documentation", "docs": "try the documentation in swagger"
    }
    return templates.TemplateResponse("index.html", {"request": request, "data": data})


@app.get("/log", include_in_schema=False, operation_id="super_admin_log", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def log(request: Request, admin: AdminApp = Depends(get_current_admin)):
    """ Запит на файл з логами """
    time_now = correct_time()
    headers = dict(request.headers)
    ip_address, user_agent = headers.get('x-forwarded-for'), headers.get('user-agent')
    logger.info(f"{time_now}: {admin.login} enter in '/log'\nip_address: {ip_address}\nuser_agent: {user_agent}")
    try:
        logger.debug(f"send log in Telegram")
        for file in [file_log_fast_api, file_log_tel_bot]:
            try:
                with open(file=file, mode='rb') as document:
                    r = await bot.send_document(chat_id=sb_telegram_id, document=document, disable_notification=False)
                    logger.info(f"{time_now}: send log in Telegram for {admin.login}={r}")
            except Exception as e:
                text = f"ERROR in sending file '{file}':\n{e}"
                await bot.send_message(chat_id=sb_telegram_id, text=text, disable_notification=False)
            await asyncio.sleep(1)
        return JSONResponse({"success": True, "msg": "Check your Telegram!"})
    except Exception as e:
        logger.error(e)
        detail = [{"success": False, "msg": f"{time_now}: send log in Telegram for '{admin.login}' = ERROR:'{e}'"}]
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


@app.get("/docs", include_in_schema=False, operation_id="super_admin_docs")
@limiter.limit("60/minute")
async def docs(request: Request, admin: AdminApp = Depends(get_current_admin)):
    time_now = correct_time()
    headers = dict(request.headers)
    ip_address, user_agent, page = headers.get('x-forwarded-for'), headers.get('user-agent'), 'docs'
    logger.info(f"{time_now}: '{admin.login}' in page '{page}':\nip_address: {ip_address}\nuser_agent: {user_agent}")
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/redoc", include_in_schema=False, operation_id="super_admin_redoc")
@limiter.limit("60/minute")
async def redoc(request: Request, admin: AdminApp = Depends(get_current_admin)):
    time_now = correct_time()
    headers = dict(request.headers)
    ip_address, user_agent, page = headers.get('x-forwarded-for'), headers.get('user-agent'), 'redoc'
    logger.info(f"{time_now}: '{admin.login}' in page '{page}':\nip_address: {ip_address}\nuser_agent: {user_agent}")
    return get_redoc_html(openapi_url="/openapi.json", title="redoc")


@app.get("/openapi.json", include_in_schema=False, operation_id="super_admin_open_api_endpoint")
@limiter.limit("60/minute")
async def open_api_endpoint(request: Request, admin: AdminApp = Depends(get_current_admin)):
    time_now = correct_time()
    headers = dict(request.headers)
    ip_address, user_agent, page = headers.get('x-forwarded-for'), headers.get('user-agent'), 'open_api_endpoint'
    logger.info(f"{time_now}: '{admin.login}' in page '{page}':\nip_address: {ip_address}\nuser_agent: {user_agent}")
    return get_openapi(title="FastAPI", version="1.0.0", routes=app.routes)
