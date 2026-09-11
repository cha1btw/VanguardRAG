import uuid
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.schemas.document import DocumentChunk


class TextChunkerService:

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def split_text(self, text: str, filename: str) -> List[DocumentChunk]:
        raw_chunks = self.splitter.split_text(text)
        chunks = []

        for idx, chunk_text in enumerate(raw_chunks):
            chunk_id = str(uuid.uuid4())
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_name=filename,
                    content=chunk_text,
                    metadata={
                        "chunk_index": idx,
                        "total_chunks": len(raw_chunks),
                        "source": filename,
                    },
                )
            )
        return chunks


chunker_service = TextChunkerService()
