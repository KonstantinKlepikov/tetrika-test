from fastapi import APIRouter
from app.api.api_v1.endpoints import files


api_router = APIRouter()


api_router.include_router(
    files.router, prefix="", tags=['files', ]
        )
