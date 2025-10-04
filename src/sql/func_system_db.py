from asyncio import sleep
from typing import Optional

from sqlalchemy.future import select

from src.service.loggers.py_logger_fast_api import get_logger
from src.sql.connect import DBSession
from src.sql.models import SystemData

logger = get_logger(__name__)


async def create_system_data(
    title: str, data_digital: int = None, data_text: str = None, data_status: bool = None
) -> Optional[SystemData]:
    """Create SystemData in DataBase"""
    for n in range(3):
        try:
            logger.debug(f"create_system_data(title={title}, ***)")
            async with DBSession() as session:
                async with session.begin():
                    system_data = SystemData(
                        title=title, data_digital=data_digital, data_text=data_text, data_status=data_status
                    )
                    await session.merge(instance=system_data)
                    await session.commit()
                    return system_data
        except Exception as e:
            logger.error(f"Attempt={n+1}: {e}")
    return None


async def get_system_data(title: str) -> Optional[SystemData]:
    """Get SystemData by str: title"""
    for n in range(3):
        try:
            logger.debug(f"get_system_data(title={title})")
            async with DBSession() as session:
                query = select(SystemData).filter_by(title=title)
                result = await session.execute(query)
                doc = result.scalar()
                return doc
        except Exception as e:
            logger.error(f"Attempt {n + 1}: {e}")
            await sleep(0.5)
    return None


# import asyncio
# async def test():
#     r = await create_system_data(title="check_report", data_text="15:00")
#     doc = await get_system_data(title="check_report")
#     print(doc.data_text)
#     print(doc.data_digital)
# asyncio.run(test())
