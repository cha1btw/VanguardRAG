from fastapi import APIRouter, File, HTTPException, UploadFile
from app.schemas.document import IngestResponse
from app.services.chunker import chunker_service
from app.services.embedder import embedder_service
from app.services.parser import parser_service
from app.services.qdrant_client import qdrant_service

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    text = await parser_service.parse_file(file)
    if not text.strip():
        raise HTTPException(
            status_code=400, detail="Файл пуст или не содержит текста"
        )

    chunks = chunker_service.split_text(text, filename=file.filename)
    texts_to_embed = [c.content for c in chunks]
    embeddings = await embedder_service.embed_documents(texts_to_embed)
    await qdrant_service.upsert_chunks(chunks, embeddings)

    return IngestResponse(
        filename=file.filename,
        total_chunks=len(chunks),
        message=f"Документ успешно обработан. Загружено {len(chunks)} чанков.",
    )
