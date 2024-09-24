from typing import Optional, Union
from sqlalchemy.future import select
from src.sql.connect import DBSession
from src.sql.models import AdminApp
from src.service.loggers.py_logger_fast_api import get_logger

logger = get_logger(__name__)

models = {'admin': AdminApp}


async def get_admin(login: str, password: str) -> Optional[Union[AdminApp]]:
    """ Get user from DataBase by 'login' and 'password' """
    for n in range(3):
        try:
            logger.debug(f'get_admin(login={login}, password=***)')
            async with DBSession() as session:
                admin = await session.execute(
                    select(AdminApp).filter(AdminApp.login==login, AdminApp.password==password)
                )
                admin = admin.scalar()
                if admin:
                    return admin
                else:
                    return
        except Exception as e:
            logger.error(f"attempt={n + 1} error: {e}")
    return