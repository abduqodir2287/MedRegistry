from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.configs.config import settings


class Base(DeclarativeBase):
	engine = create_async_engine(settings.DATABASE_URL, echo=True)
	async_session = async_sessionmaker(engine)

