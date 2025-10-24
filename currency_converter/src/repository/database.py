from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String
from sqlalchemy.types import Enum as SQLAlchemyEnum

from src.config import settings
from src.custom_types import ExchangeStatus, Str3, Str128


engine = create_async_engine(
    settings.database_url,
    echo=True,
)

session_maker = async_sessionmaker(engine)


class Base(DeclarativeBase):
    type_annotation_map = {
        ExchangeStatus: SQLAlchemyEnum(ExchangeStatus, name="exchange_status"),
        Str3: String(3),
        Str128: String(128),
    }


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
