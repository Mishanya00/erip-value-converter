import asyncio
import logging
from datetime import datetime, time
from zoneinfo import ZoneInfo

from src.repository.database import session_maker
from src.converter.repositories import ExchangeRateRepository
from src.client.currency_rate_client import CurrencyRateClient
from src.converter.api.v1.schemas import ExchangeRateBaseSchema
from src.config import settings


MINSK_TZ = ZoneInfo(settings.TIMEZONE)
FETCH_TIME = time(0, 0)
CUTOFF_TIME = time(23, 0)

RETRY_INTERVALS_MINUTES = [1, 2, 5, 10, 15, 30, 60, 120, 180, 240, 300, 360, 420]

logger = logging.getLogger("scheduler")


async def fetch_and_store_rates_job():
    today_minsk = datetime.now(MINSK_TZ).date()
    logger.info(f"Starting currency rate fetch job for date: {today_minsk}")

    attempt = 0
    while True:
        logger.info(f"Attempt {attempt + 1}: Creating new database session.")
        try:
            async with session_maker() as session:
                repo = ExchangeRateRepository(session)

                if attempt == 0:
                    rates_exist = await repo.is_present_by_date(today_minsk)
                    if rates_exist:
                        logger.info(f"Rates for {today_minsk} already exist. Job finished.")
                        return

                async with CurrencyRateClient(base_url=settings.EXTERNAL_API_URL) as aclient:
                    currency_rates = await aclient.get_rates()

                rates_to_create = [
                    ExchangeRateBaseSchema(
                        cur_id=cr.id,
                        cur_abbreviation=cr.abbreviation,
                        cur_scale=cr.scale,
                        cur_name=cr.name,
                        cur_official_rate=cr.rate,
                        cur_date=cr.timestamp.date()
                    ) for cr in currency_rates
                ]

                await repo.insert_many_rates(rates_to_create)

                await session.commit()

            logger.info(f"Stored {len(rates_to_create)} rates on attempt {attempt + 1}.")
            return

        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            attempt += 1

            if attempt > len(RETRY_INTERVALS_MINUTES):
                logger.critical("All retry attempts failed. Try manual data fetching.")
                return

            if datetime.now(MINSK_TZ).time() >= CUTOFF_TIME:
                logger.warning("Cutoff time reached. Stopping retries for today.")
                return

            sleep_minutes = RETRY_INTERVALS_MINUTES[attempt - 1]
            logger.info(f"Will retry in {sleep_minutes} minutes...")
            await asyncio.sleep(sleep_minutes * 60)
