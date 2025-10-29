import uuid
from typing import Annotated
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import text, UUID, Integer, DateTime, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from src.config import settings
from src.custom_types import Str3, Str128, ExchangeStatus
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

    def __repr__(self) -> str:
        return (
            f"<ExchangeRate: {self.cur_id} - {self.cur_abbreviation} - {self.cur_scale} - "
            f"{self.cur_name} - {self.cur_official_rate}>"
        )


class Exchange(Base):
    __tablename__ = "exchange"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)

    source_cur_abbreviation: Mapped[Str3] = mapped_column(nullable=False)
    target_cur_abbreviation: Mapped[Str3] = mapped_column(nullable=True)
    source_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(19, 28), nullable=False)
    status: Mapped[ExchangeStatus] = mapped_column(nullable=False)

    created_at: Mapped[created_at_type]
    modified_at: Mapped[modified_at_type]

    def __repr__(self) -> str:
        return (
            f"<Exchange {self.id}: {self.source_cur_abbreviation} -> {self.target_cur_abbreviation}:"
            f"{self.source_amount} -> {self.target_amount}. {self.rate} - {self.status}>"
        )
