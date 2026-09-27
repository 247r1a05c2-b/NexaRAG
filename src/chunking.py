def chunk_documents(documents, chunk_size=900, overlap=150):
    chunks = []
    for document in documents:
        text = " ".join(document["text"].split())
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({"text": chunk_text, "source": document["source"], "page": document["page"]})
            if end >= len(text):
                break
            start = end - overlap
    return chunks
