import sys
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.converter.api.router import converter_router
from src.converter.exceptions import BaseAppException


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await AsyncORM.create_tables() # Uncomment to use instead of migrations

    yield

    # actions after

app = FastAPI()
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
