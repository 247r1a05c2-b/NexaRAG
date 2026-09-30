from src.audit_log import list_events, record_event
from src.chunking import chunk_documents
from src.evaluation import retrieval_quality
from src.hybrid_retrieval import combine_scores
from src.llm import generate_answer, run_task
from src.self_healing import heal_knowledge_base, restore_chunk, scan_knowledge_base
from src.vector_store import add_chunks, delete_source, get_all_chunks, get_documents, get_stats, reset_collection, search


def build_index(documents):
    if not documents:
        raise ValueError("No readable text was found in the uploaded documents.")
    chunks = chunk_documents(documents)
    if not chunks:
        raise ValueError("The uploaded files did not contain usable text.")
    count = add_chunks(chunks)
    record_event("ingestion", {"documents": len(documents), "chunks_added": count})
    return count


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
    results = combine_scores(search(question, top_k=10), question)[:7]
    if not results:
        raise ValueError("The knowledge base is empty. Process documents first.")
    context, sources = format_context(results)
    answer = generate_answer(question, context, history)
    return answer, sources, results, retrieval_quality(results)


def run_document_task(task, limit=24):
    chunks = [chunk for chunk in get_all_chunks(limit=limit) if chunk.get("status", "active") == "active"]
    if not chunks:
        raise ValueError("The knowledge base is empty. Process documents first.")
    context, sources = format_context(chunks)
    return run_task(task, context), sources


def delete_document(source):
    delete_source(source)
    record_event("delete_source", {"source": source})


def list_documents():
    return get_documents()


def clear_index():
    reset_collection()
    record_event("clear_knowledge_base", {})


def stats():
    return get_stats()


def scan_knowledge_health(limit=None):
    return scan_knowledge_base(limit=limit)


def heal_knowledge_health(report, approved_issue_indexes=None):
    return heal_knowledge_base(report, approved_issue_indexes=approved_issue_indexes)


def restore_knowledge_chunk(chunk_id):
    return restore_chunk(chunk_id)


def audit_history(limit=30):
    return list_events(limit=limit)
