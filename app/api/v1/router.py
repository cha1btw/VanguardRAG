from fastapi import APIRouter
from app.api.v1.endpoints import generate, ingest, search

api_router = APIRouter()
api_router.include_router(ingest.router, prefix="/documents", tags=["Ingest"])
api_router.include_router(search.router, prefix="/documents", tags=["Search"])
api_router.include_router(
    generate.router, prefix="/documents", tags=["Generate"]
)
