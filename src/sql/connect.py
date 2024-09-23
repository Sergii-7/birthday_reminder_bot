from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import URI_DB


""" async connect with database: '/avrora_parsing' """
DATABASE_URL = f"postgresql+asyncpg://{URI_DB}"
# engine = create_async_engine(DATABASE_URL, echo=True)
engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
DBSession = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)