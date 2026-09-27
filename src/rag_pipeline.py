from src.chunking import chunk_documents
from src.evaluation import retrieval_quality
from src.hybrid_retrieval import combine_scores
from src.llm import generate_answer, run_task
from src.vector_store import add_chunks, get_all_chunks, get_stats, reset_collection, search

def build_index(documents):
    if not documents:
        raise ValueError("No readable text was found in the uploaded documents.")
    chunks = chunk_documents(documents)
    if not chunks:
        raise ValueError("The uploaded files did not contain usable text.")
    return add_chunks(chunks)

def format_context(results):
    parts = []
    sources = []
    for item in results:
        location = item["source"]
        if item["page"]:
            location += f" — page {item['page']}"
        parts.append(f"[Source: {location}]\n{item['text']}")
        if location not in sources:
            sources.append(location)
    return "\n\n".join(parts), sources

def answer_question(question, history=None):
    results = combine_scores(search(question, top_k=8), question)[:6]
    if not results:
        raise ValueError("The knowledge base is empty. Process documents first.")
    context, sources = format_context(results)
    answer = generate_answer(question, context, history)
    return answer, sources, results, retrieval_quality(results)

def run_document_task(task, limit=24):
    chunks = get_all_chunks(limit=limit)
    if not chunks:
        raise ValueError("The knowledge base is empty. Process documents first.")
    context, sources = format_context(chunks)
    return run_task(task, context), sources

def clear_index():
    reset_collection()

def stats():
    return get_stats()
