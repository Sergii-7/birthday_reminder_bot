from typing import Optional, Union

from sqlalchemy.future import select

from src.service.loggers.py_logger_fast_api import get_logger
from src.sql.connect import DBSession
from src.sql.models import AdminApp
from src.sql.tool_db import retry_on_db_error

logger = get_logger(__name__)

models = {"admin": AdminApp}


@retry_on_db_error()
async def get_admin(login: str, password: str) -> Optional[Union[AdminApp]]:
    """Get user from DataBase by 'login' and 'password'"""
    logger.debug(f"get_admin(login={login}, password=***)")
    async with DBSession() as session:
        admin = await session.execute(select(AdminApp).filter(AdminApp.login == login, AdminApp.password == password))
        admin = admin.scalar()
        return admin if admin else None
