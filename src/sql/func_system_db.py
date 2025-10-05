from typing import Optional

from sqlalchemy.future import select

from src.service.loggers.py_logger_fast_api import get_logger
from src.sql.connect import DBSession
from src.sql.models import SystemData
from src.sql.tool_db import retry_on_db_error

logger = get_logger(__name__)


@retry_on_db_error()
async def create_system_data(
    title: str, data_digital: int = None, data_text: str = None, data_status: bool = None
) -> Optional[SystemData]:
    """Create SystemData in DataBase"""
    logger.debug(f"create_system_data(title={title}, ***)")
    async with DBSession() as session:
        async with session.begin():
            system_data = SystemData(
                title=title, data_digital=data_digital, data_text=data_text, data_status=data_status
            )
            await session.merge(instance=system_data)
            await session.commit()
            return system_data


@retry_on_db_error()
async def get_system_data(title: str) -> Optional[SystemData]:
    """Get SystemData by str: title"""
    logger.debug(f"get_system_data(title={title})")
    async with DBSession() as session:
        query = select(SystemData).filter_by(title=title)
        result = await session.execute(query)
        doc = result.scalar()
        return doc


async def _demo():
    """Demo function to get SystemData."""
    doc = await get_system_data(title="check_report")
    if doc:
        print(doc.data_text)
        print(doc.data_digital)
    else:
        print("No document found.")


if __name__ == "__main__":
    """Run demo if this file is executed directly."""
    import asyncio

    asyncio.run(_demo())
