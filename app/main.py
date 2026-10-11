from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from app.api.v1.router import api_router
from app.config import settings
from app.core.exceptions import OllamaUnavailableError
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

@app.exception_handler(OllamaUnavailableError)
async def ollama_unavailable_handler(
    request: Request, error: OllamaUnavailableError
):
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Ollama is unavailable. Make sure it is running and "
            f"the models '{settings.LLM_MODEL}' and "
            f"'{settings.EMBEDDING_MODEL}' are pulled."
        },
    )


# Подключаем роуты v1 к основному приложению
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check():
    try:
        await qdrant_service.check_connection()
    except Exception as error:
        raise HTTPException(
            status_code=503, detail="Qdrant is unavailable"
        ) from error

    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "dependencies": {"qdrant": "ok"},
    }
