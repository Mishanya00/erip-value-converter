import uuid
from decimal import Decimal
from typing import Annotated
from datetime import date, datetime

from pydantic import BaseModel, Field, ConfigDict


class ExchangeRateBaseSchema(BaseModel):
    cur_id: Annotated[int, Field(description="Numeric currency code")]
    cur_abbreviation: Annotated[str, Field(description="Three letter currency code")]
    cur_scale: Annotated[int, Field(description="Amount of currency units")]
    cur_name: Annotated[str, Field(description="Currency name")]
    cur_official_rate: Annotated[
        Decimal,
        Field(description="Currency official exchange rate in belarusian rubles"),
    ]
    cur_date: Annotated[date, Field(description="Date of this exchange rate")]

    model_config = ConfigDict(from_attributes=True)


class ExchangeRateReadSchema(ExchangeRateBaseSchema):
    id: Annotated[uuid.UUID, Field(description="Exchange rate id")]
    created_at: Annotated[datetime, Field(description="Exchange rate creation date")]
    modified_at: Annotated[
        datetime, Field(description="Exchange rate modification date")
    ]


class ExchangeMoneyRequestSchema(BaseModel):
    source_cur_amount: Annotated[Decimal, Field(description="Source currency amount")]
    source_cur_abbreviation: Annotated[
        str, Field(description="Three letter source currency code")
    ]
    target_cur_abbreviation: Annotated[
        str, Field(description="Three letter target currency code")
    ]


class ExchangeMoneyResponseSchema(BaseModel):
    target_cur_amount: Annotated[Decimal, Field(description="Quote currency amount")]
    exchange_rate: Annotated[Decimal, Field(description="Exchange rate")]
    transaction_uuid: Annotated[uuid.UUID, Field(description="Transaction UUID")]
