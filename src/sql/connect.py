from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import URI_DB

""" async connect with database: '/birthday_bot' """
# engine = create_async_engine(url=f"postgresql+asyncpg://{URI_DB}", echo=True)
engine = create_async_engine(url=f"postgresql+asyncpg://{URI_DB}", pool_pre_ping=True)
DBSession = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)