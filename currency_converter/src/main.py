from fastapi import FastAPI

from src.converter.api.router import converter_router

app = FastAPI()

app.include_router(converter_router, prefix="/converter", tags=["converter"])


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
