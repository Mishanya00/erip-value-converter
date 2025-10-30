import uuid
from datetime import date

from sqlalchemy import select, insert, case, update

from src.custom_types import ExchangeStatus
from src.converter.api.v1.schemas import ExchangeRateBaseSchema, ExchangeBaseSchema
from src.repository.database import BaseRepository
from src.converter.models import ExchangeRate, Exchange


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

    async def select_rate_by_cur_abbreviation_and_date(
        self, cur_abbreviation: str, cur_date: date
    ) -> ExchangeRate:
        result = await self.session.execute(
            select(ExchangeRate).filter(
                (ExchangeRate.cur_abbreviation == cur_abbreviation)
                & (ExchangeRate.cur_date == cur_date)
            )
        )
        return result.scalar_one_or_none()

    async def select_two_rates_by_cur_abbreviations_and_date(
        self, source_cur_abbreviation, target_cur_abbreviation, cur_date: date
    ) -> list[ExchangeRate]:
        result = await self.session.execute(
            select(ExchangeRate)
            .filter(
                (
                    (ExchangeRate.cur_abbreviation == source_cur_abbreviation)
                    | (ExchangeRate.cur_abbreviation == target_cur_abbreviation)
                )
                & (ExchangeRate.cur_date == cur_date)
            )
            .order_by(
                case(
                    (ExchangeRate.cur_abbreviation == source_cur_abbreviation, 1),
                    (ExchangeRate.cur_abbreviation == target_cur_abbreviation, 2),
                    else_=3,
                )
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


class ExchangeRepository(BaseRepository):
    async def insert_new_exchange(self, exchange: ExchangeBaseSchema):
        if not exchange:
            return None

        statement = insert(Exchange).values(exchange.model_dump()).returning(Exchange)
        result = await self.session.execute(statement)

        inserted_exchange = result.scalar_one_or_none()

        await self.session.commit()
        return inserted_exchange

    async def select_exchange_by_id(self, id: uuid.UUID):
        exchange = await self.session.execute(
            select(Exchange).filter(Exchange.id == id)
        )
        return exchange.scalar_one_or_none()

    async def update_exchange_status(
        self, exchange_id: uuid.UUID, new_status: ExchangeStatus
    ) -> Exchange | None:
        stmt = (
            update(Exchange)
            .where(Exchange.id == exchange_id)
            .values(status=new_status)
            .returning(Exchange)
        )
        try:
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.scalar_one_or_none()
        except Exception:
            await self.session.rollback()
            raise
