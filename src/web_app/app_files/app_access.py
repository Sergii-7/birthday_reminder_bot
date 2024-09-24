from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from src.sql.func_app_db import get_admin
from src.sql.func_db import get_user_by_login
from src.service.loggers.py_logger_fast_api import get_logger

logger = get_logger(__name__)

security = HTTPBasic()


async def get_current_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """ Check if user == admin or not """
    admin = await get_admin(login=credentials.username, password=credentials.password)
    if not admin or not admin.status:
        logger.error(f"status.HTTP_401_UNAUTHORIZED: '{credentials.username}' and his password are not valid!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return admin


async def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """ Check if user == admin or not """
    try:
        logger.debug('get_current_user()')
        user_login = await get_user_by_login(
            telegram_id=int(credentials.telegram_id), password=credentials.user_password)
        if user_login:
            return user_login
    except Exception as e:
        logger.error(e)
    logger.error(f"status.HTTP_401_UNAUTHORIZED: 'Incorrect telegram_id or password'")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect telegram_id or password",
        headers={"WWW-Authenticate": "Basic"},
    )

