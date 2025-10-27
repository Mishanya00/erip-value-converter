from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field


class ExternalAPIExchangeRateSchema(BaseModel):
    id: Annotated[int, Field(alias='Cur_ID')]
    timestamp: Annotated[datetime, Field(alias='Date')]
    abbreviation: Annotated[str, Field(alias='Cur_Abbreviation')]
    scale: Annotated[int, Field(alias='Cur_Scale')]
    name: Annotated[str, Field(alias='Cur_Name')]
    rate: Annotated[Decimal, Field(alias='Cur_OfficialRate')]
