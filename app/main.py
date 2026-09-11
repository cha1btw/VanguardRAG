from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.router import api_router
from app.config import settings
from app.services.qdrant_client import qdrant_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    await qdrant_service.init_collection()
    yield
    await qdrant_service.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# Подключаем роуты v1 к основному приложению
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}
