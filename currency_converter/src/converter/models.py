import uuid
from typing import Annotated
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import text, UUID, Integer, DateTime, Date, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from src.config import settings
from src.custom_types import Str3, Str128
from src.repository.database import Base


timezone_default = text("TIMEZONE(:tz, now())").bindparams(tz=settings.TIMEZONE)

created_at_type = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=timezone_default,
    ),
]

modified_at_type = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=timezone_default,
        onupdate=timezone_default,
        nullable=False,
    ),
]


class ExchangeRate(Base):
    __tablename__ = "exchange_rate"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)

    cur_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cur_abbreviation: Mapped[Str3] = mapped_column(nullable=False)
    cur_scale: Mapped[int] = mapped_column(Integer, nullable=False)
    cur_name: Mapped[Str128] = mapped_column(nullable=True)
    cur_official_rate: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    cur_date: Mapped[date] = mapped_column(Date, nullable=False)

    created_at: Mapped[created_at_type]
    modified_at: Mapped[modified_at_type]
