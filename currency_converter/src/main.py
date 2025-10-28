import sys
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.scheduler import fetch_and_store_rates_job, MINSK_TZ, FETCH_TIME, CUTOFF_TIME
from src.converter.api.router import converter_router
from src.converter.exceptions import BaseAppException


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler(timezone=MINSK_TZ)

    scheduler.add_job(
        fetch_and_store_rates_job,
        trigger='cron',
        # minute='*',
        hour=FETCH_TIME.hour,
        minute=FETCH_TIME.minute,
        id="daily_national_bank_api_data_fetch",
        replace_existing=True,
    )

    scheduler.add_job(
        fetch_and_store_rates_job,
        trigger='date',
        id="startup_national_bank_api_data_fetch",
    )

    scheduler.start()

    yield

    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)
app.include_router(converter_router, prefix="/converter", tags=["converter"])


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

logger.info("Logger is initialized")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.exception_handler(BaseAppException)
async def app_exception_handler(request: Request, error: BaseAppException):
    return JSONResponse(status_code=error.status_code, content={"error": error.message})
