from typing import Annotated

from pydantic import BaseModel, Field


class ExchangeRateBaseSchema(BaseModel):
    cur_id: Annotated[int, Field(description="Numeric currency code")]
    cur_abbreviation: Annotated[str, Field(description="Three letter currency code")]
    cur_scale: Mapped[int] = Annotated[int, Field(description="Amount of ")]
    cur_name: Mapped[Str128] = mapped_column(nullable=True)
    cur_official_rate: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    cur_date: Mapped[date] = mapped_column(Date, nullable=False)

    model_config = ConfigDict(from_attributes=True)
