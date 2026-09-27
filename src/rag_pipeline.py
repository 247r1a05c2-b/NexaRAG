from src.chunking import chunk_documents
from src.llm import generate_answer
from src.vector_store import add_chunks, reset_collection, search

def build_index(documents):
    if not documents:
        raise ValueError("No readable text was found in the uploaded documents.")
    reset_collection()
    chunks = chunk_documents(documents)
    return add_chunks(chunks)

def answer_question(question):
    results = search(question, top_k=5)
    if not results:
        raise ValueError("The knowledge base is empty. Process documents first.")

    context_parts = []
    sources = []
    for item in results:
        location = item["source"]
        if item["page"]:
            location += f" — page {item['page']}"
        context_parts.append(f"[Source: {location}]\n{item['text']}")
        if location not in sources:
            sources.append(location)

    answer = generate_answer(question, "\n\n".join(context_parts))
    return answer, sources

def clear_index():
    reset_collection()
