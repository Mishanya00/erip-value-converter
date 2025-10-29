from datetime import date

from sqlalchemy import select, insert

from src.converter.api.v1.schemas import ExchangeRateBaseSchema
from src.repository.database import BaseRepository
from src.converter.models import ExchangeRate


class ExchangeRateRepository(BaseRepository):
    async def is_present_by_date(self, cur_date: date) -> bool:
        result = await self.session.execute(
            select(ExchangeRate).filter(ExchangeRate.cur_date == cur_date)
        )
        if result.scalars().first():
            return True
        return False

    async def select_rates_by_cur_date(self, cur_date: date) -> list[ExchangeRate]:
        result = await self.session.execute(
            select(ExchangeRate).filter(ExchangeRate.cur_date == cur_date)
        )
        return list(result.scalars().all())

    async def select_rate_by_cur_abbreviation(
        self, cur_abbreviation: str
    ) -> ExchangeRate:
        result = await self.session.execute(
            select(ExchangeRate).filter(
                ExchangeRate.cur_abbreviation == cur_abbreviation
            )
        )
        return result.scalar_one_or_none()

    async def select_two_rates_by_cur_abbreviations(
        self, source_cur_abbreviation, target_cur_abbreviation
    ) -> list[ExchangeRate]:
        result = await self.session.execute(
            select(ExchangeRate).filter(
                (ExchangeRate.cur_abbreviation == source_cur_abbreviation)
                | (ExchangeRate.cur_abbreviation == target_cur_abbreviation)
            )
        )

        return list(result.scalars().all())

    async def insert_many_rates(self, rates: list[ExchangeRateBaseSchema]):
        if not rates:
            return []

        values_to_insert = [rate.model_dump() for rate in rates]
        statement = (
            insert(ExchangeRate).values(values_to_insert).returning(ExchangeRate)
        )
        result = await self.session.execute(statement)

        inserted_rows = list(result.scalars().all())

        await self.session.commit()

        return inserted_rows
