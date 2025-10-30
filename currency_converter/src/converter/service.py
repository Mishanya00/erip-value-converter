import logging
import uuid
from datetime import datetime, date
from zoneinfo import ZoneInfo
from decimal import Decimal, ROUND_HALF_EVEN

from tenacity import RetryError
from babel.numbers import get_currency_precision

from src.converter.api.v1.schemas import (
    ExchangeRateBaseSchema,
    ExchangeBaseSchema,
    ExchangeMoneyResponseSchema,
    ExchangeActionResponseSchema,
    AggregatedExchangeDataRequestSchema,
)
from src.converter.repositories import ExchangeRateRepository, ExchangeRepository
from src.converter.exceptions import (
    ExternalAPIRequestError,
    CurrencyNotSpecifiedError,
    IdenticalCurrenciesSpecifiedError,
    CurrencyDoesNotExistError,
    CurrencyAmountNotSpecifiedError,
    CurrencyAmountInvalidValueError,
    ExchangeDoesNotExistError,
    InvalidExchangeAction,
)
from src.config import settings
from src.client.currency_rate_client import CurrencyRateClient
from src.client.schemas import ExternalAPIExchangeRateSchema
from src.custom_types import ExchangeStatus, ExchangeAction
from src.exceptions import InternalServerException, BaseAppException


"""
    settings.NATIONAL_CURRENCY -> OTHER: purchase
    OTHER -> settings.NATIONAL_CURRENCY: sale
    OTHER -> OTHER: sale then purchase
"""


class CurrencyConverterService:
    def __init__(
        self,
        exchange_rate_repo: ExchangeRateRepository,
        exchange_repo: ExchangeRepository,
    ):
        self.timezone = ZoneInfo(settings.TIMEZONE)
        self.logger = logging.getLogger(__name__)
        self.exchange_rate_repo = exchange_rate_repo
        self.exchange_repo = exchange_repo

    @property
    def date(self) -> date:
        return datetime.now(self.timezone).date()

    @staticmethod
    def round_currency(value: Decimal, currency_code: str):
        precision = get_currency_precision(currency_code)
        rounded = value.quantize(
            Decimal("0." + "0" * precision), rounding=ROUND_HALF_EVEN
        )
        return rounded

    async def get_currency_rates_request(
        self, period: int = 0
    ) -> list[ExternalAPIExchangeRateSchema]:
        async with CurrencyRateClient(base_url=settings.EXTERNAL_API_URL) as aclient:
            try:
                currency_rates: list[
                    ExternalAPIExchangeRateSchema
                ] = await aclient.get_rates(period)
            except RetryError as e:
                self.logger.exception(f"Failed to get currency rates: {e}")
                raise ExternalAPIRequestError
        return currency_rates

    async def get_today_currency_rates(self):
        rates = await self.exchange_rate_repo.select_rates_by_cur_date(self.date)
        if not rates:
            async with CurrencyRateClient(
                base_url=settings.EXTERNAL_API_URL
            ) as aclient:
                try:
                    currency_rates: list[
                        ExternalAPIExchangeRateSchema
                    ] = await aclient.get_rates()

                    rates_to_create: list[ExchangeRateBaseSchema] = [
                        ExchangeRateBaseSchema(
                            cur_id=currency_rate.id,
                            cur_abbreviation=currency_rate.abbreviation,
                            cur_scale=currency_rate.scale,
                            cur_name=currency_rate.name,
                            cur_official_rate=currency_rate.rate,
                            cur_date=currency_rate.timestamp.date(),
                        )
                        for currency_rate in currency_rates
                    ]

                    rates = await self.exchange_rate_repo.insert_many_rates(
                        rates_to_create
                    )
                except RetryError as e:
                    self.logger.exception(f"Failed to get currency rates: {e}")
                    raise ExternalAPIRequestError
        return rates

    async def execute_currency_exchange(
        self, source_amount: Decimal, source_currency: str, target_currency: str
    ) -> ExchangeMoneyResponseSchema:
        if not source_currency or not target_currency:
            raise CurrencyNotSpecifiedError

        if source_currency == target_currency:
            raise IdenticalCurrenciesSpecifiedError

        if not source_amount:
            raise CurrencyAmountNotSpecifiedError

        if source_amount <= 0:
            raise CurrencyAmountInvalidValueError

        if source_currency == settings.NATIONAL_CURRENCY:
            # Purchase operation
            target_currency_info = (
                await self.exchange_rate_repo.select_rate_by_cur_abbreviation_and_date(
                    target_currency, self.date
                )
            )
            if not target_currency_info:
                raise CurrencyDoesNotExistError

            exchange_rate = (
                target_currency_info.cur_scale
                * Decimal("1.0")
                / target_currency_info.cur_official_rate
            )

            target_amount = source_amount * exchange_rate

        elif target_currency == settings.NATIONAL_CURRENCY:
            # sale operation
            source_currency_info = (
                await self.exchange_rate_repo.select_rate_by_cur_abbreviation_and_date(
                    source_currency, self.date
                )
            )
            if not source_currency_info:
                raise CurrencyDoesNotExistError

            exchange_rate = (
                source_currency_info.cur_scale * source_currency_info.cur_official_rate
            )

            target_amount = source_amount * exchange_rate
        else:
            currencies_info = await self.exchange_rate_repo.select_two_rates_by_cur_abbreviations_and_date(
                source_currency, target_currency, self.date
            )
            if not currencies_info or len(currencies_info) < 2:
                raise CurrencyDoesNotExistError

            source_currency_info = currencies_info[0]
            target_currency_info = currencies_info[1]

            # sell source currency to buy national one
            intermediate_exchange_rate = (
                source_currency_info.cur_scale * source_currency_info.cur_official_rate
            )
            intermediate_amount = source_amount * intermediate_exchange_rate

            # buy target currency using bought national currency
            exchange_rate = (
                target_currency_info.cur_scale
                * Decimal("1.0")
                / target_currency_info.cur_official_rate
            )

            target_amount = intermediate_amount * exchange_rate

        inserted_exchange_transaction = await self.exchange_repo.insert_new_exchange(
            ExchangeBaseSchema(
                source_cur_abbreviation=source_currency,
                target_cur_abbreviation=target_currency,
                source_amount=source_amount,
                target_amount=target_amount,
                rate=exchange_rate,
                status=ExchangeStatus.PENDING,
            )
        )

        if not inserted_exchange_transaction:
            raise InternalServerException("Money exchange failed.")

        rounded_target_amount = self.round_currency(target_amount, target_currency)

        return ExchangeMoneyResponseSchema(
            target_cur_amount=rounded_target_amount,
            exchange_rate=exchange_rate,
            transaction_uuid=inserted_exchange_transaction.id,
        )

    async def execute_exchange_action(
        self, transaction_uuid: uuid.UUID, action: ExchangeAction
    ) -> ExchangeActionResponseSchema:
        if not action or action not in (
            ExchangeAction.CONFIRM,
            ExchangeAction.CANCEL,
        ):
            raise InvalidExchangeAction

        match action:
            case ExchangeAction.CONFIRM:
                status = ExchangeStatus.CONFIRMED
            case ExchangeAction.CANCEL:
                status = ExchangeStatus.CANCELED

        exchange = await self.exchange_repo.select_exchange_by_id(transaction_uuid)

        if not exchange:
            raise ExchangeDoesNotExistError

        if exchange.status != ExchangeStatus.PENDING:
            raise BaseAppException(message="Exchange already handled!", status_code=400)

        result = await self.exchange_repo.update_exchange_status(
            transaction_uuid, status
        )
        if result:
            return ExchangeActionResponseSchema(
                id=result.id,
                status=result.status,
            )
        raise InternalServerException("Exchange status update failed!")

    async def get_confirmed_exchanges_by_time_period(
        self, exchanges_info: AggregatedExchangeDataRequestSchema
    ):
        aggregated_data = await self.exchange_repo.get_aggregated_exchange_report_by_time_period_and_currency(
            exchanges_info.start_datetime,
            exchanges_info.end_datetime,
            exchanges_info.currency_code,
        )

        for currency in aggregated_data:
            currency.total_sent = self.round_currency(
                currency.total_sent, currency.currency_code
            )
            currency.total_received = self.round_currency(
                currency.total_received, currency.currency_code
            )

        return aggregated_data
