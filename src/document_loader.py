import io
from pathlib import Path
from pypdf import PdfReader
from docx import Document
from pptx import Presentation
import fitz
from PIL import Image
import pytesseract

def load_uploaded_file(uploaded_file):
    name = uploaded_file.name
    suffix = Path(name).suffix.lower()
    data = uploaded_file.getvalue()

    if suffix == ".pdf":
        reader = PdfReader(io.BytesIO(data))
        documents = []
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                documents.append({"text": text, "source": name, "page": page_number, "method": "text"})
            else:
                pdf = fitz.open(stream=data, filetype="pdf")
                rendered = pdf[page_number - 1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
                image = Image.frombytes("RGB", [rendered.width, rendered.height], rendered.samples)
                ocr_text = pytesseract.image_to_string(image)
                if ocr_text.strip():
                    documents.append({"text": ocr_text, "source": name, "page": page_number, "method": "ocr"})
                pdf.close()
        return documents

    if suffix == ".docx":
        document = Document(io.BytesIO(data))
        parts = [p.text for p in document.paragraphs if p.text.strip()]
        for table in document.tables:
            for row in table.rows:
                parts.append(" | ".join(cell.text.strip() for cell in row.cells))
        text = "\n".join(parts)
        return [{"text": text, "source": name, "page": None, "method": "text"}] if text.strip() else []

    if suffix == ".pptx":
        presentation = Presentation(io.BytesIO(data))
        documents = []
        for slide_number, slide in enumerate(presentation.slides, start=1):
            parts = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    parts.append(shape.text)
                if getattr(shape, "has_table", False):
                    for row in shape.table.rows:
                        parts.append(" | ".join(cell.text.strip() for cell in row.cells))
            text = "\n".join(parts)
            if text.strip():
                documents.append({"text": text, "source": name, "page": slide_number, "method": "text"})
        return documents

    if suffix == ".txt":
        text = data.decode("utf-8", errors="ignore")
        return [{"text": text, "source": name, "page": None, "method": "text"}] if text.strip() else []

    raise ValueError(f"Unsupported file type: {suffix}")
