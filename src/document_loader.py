import io
from pathlib import Path
from pypdf import PdfReader
from docx import Document

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
                documents.append({"text": text, "source": name, "page": page_number})
        return documents

    if suffix == ".docx":
        document = Document(io.BytesIO(data))
        text = "\n".join(p.text for p in document.paragraphs if p.text.strip())
        return [{"text": text, "source": name, "page": None}] if text.strip() else []

    if suffix == ".txt":
        text = data.decode("utf-8", errors="ignore")
        return [{"text": text, "source": name, "page": None}] if text.strip() else []

    raise ValueError(f"Unsupported file type: {suffix}")
