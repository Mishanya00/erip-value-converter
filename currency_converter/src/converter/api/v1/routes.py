from fastapi import APIRouter


converter_router_v1 = APIRouter()


@converter_router_v1.get("/")
async def root():
    return {"message": "Currency Converter version 1"}
