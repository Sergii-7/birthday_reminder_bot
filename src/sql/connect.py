"""Connect with DataBase 'birthday_bot'."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import URI_DB

engine = create_async_engine(url=f"postgresql+asyncpg://{URI_DB}", pool_pre_ping=True)

DBSession = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
