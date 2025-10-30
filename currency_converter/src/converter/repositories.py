import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    func,
    select,
    insert,
    case,
    update,
    union_all,
    literal_column,
    Numeric,
)

from src.custom_types import ExchangeStatus
from src.converter.api.v1.schemas import (
    ExchangeRateBaseSchema,
    ExchangeBaseSchema,
    AggregatedExchangeDataResponseSchema,
)
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

    async def select_exchanges_by_date_range(
        self,
        start_datetime: datetime,
        end_datetime: datetime,
        currency_abbreviation: str | None = None,
    ) -> list[Exchange]:
        statement = select(Exchange).where(
            Exchange.created_at.between(start_datetime, end_datetime)
        )

        if currency_abbreviation:
            statement = statement.where(
                (Exchange.source_cur_abbreviation == currency_abbreviation)
                | (Exchange.target_cur_abbreviation == currency_abbreviation)
            )

        statement = statement.order_by(Exchange.created_at.asc())

        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_aggregated_exchange_report_by_time_period_and_currency(
        self,
        start_date: datetime,
        end_date: datetime,
        currency_abbreviation: str | None = None,
    ) -> list[AggregatedExchangeDataResponseSchema]:
        received_currency_query = (
            select(
                Exchange.source_cur_abbreviation.label("currency"),
                Exchange.source_amount.label("amount_in"),
                literal_column("0").cast(Numeric).label("amount_out"),
                literal_column("1").label("tx_count"),
            )
            .where(Exchange.created_at.between(start_date, end_date))
            .where(Exchange.status == ExchangeStatus.CONFIRMED)
        )

        sent_currency_query = (
            select(
                Exchange.target_cur_abbreviation.label("currency"),
                literal_column("0").cast(Numeric).label("amount_in"),
                Exchange.target_amount.label("amount_out"),
                literal_column("1").label("tx_count"),
            )
            .where(Exchange.created_at.between(start_date, end_date))
            .where(Exchange.status == ExchangeStatus.CONFIRMED)
        )

        combined_query = union_all(
            received_currency_query, sent_currency_query
        ).subquery()

        final_statement = (
            select(
                combined_query.c.currency,
                func.sum(combined_query.c.amount_in).label("total_received"),
                func.sum(combined_query.c.amount_out).label("total_sent"),
                func.count(combined_query.c.tx_count).label("exchange_count"),
            )
            .group_by(combined_query.c.currency)
            .order_by(combined_query.c.currency)
        )

        if currency_abbreviation:
            final_statement = final_statement.where(
                combined_query.c.currency == currency_abbreviation
            )

        result = await self.session.execute(final_statement)

        # Return using schema because it's a complex query
        report_data = []
        for row in result.mappings():
            report_data.append(
                AggregatedExchangeDataResponseSchema(
                    currency_code=row["currency"],
                    total_received=row["total_received"] or Decimal("0"),
                    total_sent=row["total_sent"] or Decimal("0"),
                    exchange_count=row["exchange_count"],
                )
            )

        return report_data

    async def select_pending_exchanges(self):
        result = await self.session.execute(
            select(Exchange).where(Exchange.status == ExchangeStatus.PENDING)
        )
        return list(result.scalars().all())
