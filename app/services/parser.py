import io
import docx
from fastapi import UploadFile, HTTPException
from pypdf import PdfReader

MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024


class DocumentParserService:
    @staticmethod
    async def parse_file(file: UploadFile) -> str:
        filename = file.filename.lower()
        contents = await file.read(MAX_UPLOAD_SIZE_BYTES + 1)
        if len(contents) > MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="File exceeds the 10 MiB upload limit",
            )

        if filename.endswith((".txt", ".md")):
            return contents.decode("utf-8", errors="ignore")

        elif filename.endswith(".pdf"):
            pdf_stream = io.BytesIO(contents)
            reader = PdfReader(pdf_stream)
            text = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text.append(extracted)
            return "\n".join(text)

        elif filename.endswith(".docx"):
            docx_stream = io.BytesIO(contents)
            doc = docx.Document(docx_stream)
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Неподдерживаемый формат файла: {file.filename}. Разрешены: .pdf, .docx, .txt, .md",
            )


parser_service = DocumentParserService()
