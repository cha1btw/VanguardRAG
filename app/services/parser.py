import io
from zipfile import BadZipFile

import docx
from docx.opc.exceptions import PackageNotFoundError
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph
from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
from pypdf.errors import PdfReadError

MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024


class DocumentParserService:
    @staticmethod
    def _extract_docx_text(doc) -> str:
        """Read paragraphs and table rows in document order."""
        lines = []
        for element in doc.element.body.iterchildren():
            if element.tag == qn("w:p"):
                text = Paragraph(element, doc).text
                if text.strip():
                    lines.append(text)
            elif element.tag == qn("w:tbl"):
                for row in Table(element, doc).rows:
                    # A merged cell is returned once per column it spans.
                    unique_cells = []
                    for cell in row.cells:
                        if not any(cell._tc is seen._tc for seen in unique_cells):
                            unique_cells.append(cell)
                    row_text = " | ".join(
                        cell.text.strip()
                        for cell in unique_cells
                        if cell.text.strip()
                    )
                    if row_text:
                        lines.append(row_text)
        return "\n".join(lines)

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
            try:
                # utf-8-sig also strips the BOM that Windows editors add.
                return contents.decode("utf-8-sig")
            except UnicodeDecodeError as error:
                raise HTTPException(
                    status_code=400,
                    detail="Text files must be UTF-8 encoded. "
                    "Re-save the file as UTF-8 and try again.",
                ) from error

        elif filename.endswith(".pdf"):
            pdf_stream = io.BytesIO(contents)
            try:
                reader = PdfReader(pdf_stream)
                text = []
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text.append(extracted)
                return "\n".join(text)
            except PdfReadError as error:
                raise HTTPException(
                    status_code=400, detail="Unable to read this PDF file"
                ) from error

        elif filename.endswith(".docx"):
            docx_stream = io.BytesIO(contents)
            try:
                return DocumentParserService._extract_docx_text(
                    docx.Document(docx_stream)
                )
            except (BadZipFile, PackageNotFoundError) as error:
                raise HTTPException(
                    status_code=400, detail="Unable to read this DOCX file"
                ) from error

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Неподдерживаемый формат файла: {file.filename}. Разрешены: .pdf, .docx, .txt, .md",
            )


parser_service = DocumentParserService()
