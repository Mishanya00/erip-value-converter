from datetime import date
from typing import List

from sqlalchemy import select

from src.repository.database import BaseRepository
from src.converter.models import ExchangeRate


class ExchangeRateRepository(BaseRepository):
    async def get_rates_by_cur_date(self, cur_date: date) -> List[ExchangeRate]:
        result = await self.session.execute(
            select(ExchangeRate).filter(ExchangeRate.cur_date == cur_date)
        )
        return list(result.scalars().all())

    async def is_present_by_date(self, cur_date: date):
        result = await self.session.execute(
            select(ExchangeRate).filter(ExchangeRate.cur_date == cur_date)
        )
        if result.scalars().first():
            return True
        return False
