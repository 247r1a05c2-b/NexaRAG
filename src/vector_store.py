import hashlib
from datetime import datetime, timezone
import chromadb
from src.embeddings import embed_texts

DB_PATH = "data/chroma"
COLLECTION_NAME = "nexarag_documents"
_client = chromadb.PersistentClient(path=DB_PATH)

def get_collection():
    return _client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

def reset_collection():
    try:
        _client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

def add_chunks(chunks):
    collection = get_collection()
    if not chunks:
        return 0
    existing = collection.get(include=[])
    existing_ids = set(existing.get("ids", []))
    new_chunks = []
    ids = []
    for chunk in chunks:
        base = f"{chunk['source']}::{chunk.get('page', 0)}::{chunk['text']}"
        chunk_id = "chunk-" + hashlib.sha1(base.encode("utf-8")).hexdigest()
        if chunk_id in existing_ids:
            continue
        new_chunks.append(chunk)
        ids.append(chunk_id)
    if not new_chunks:
        return 0
    embeddings = embed_texts([chunk["text"] for chunk in new_chunks])
    now = datetime.now(timezone.utc).isoformat()
    metadatas = [
        {
            "source": chunk["source"],
            "page": chunk["page"] if chunk["page"] is not None else 0,
            "method": chunk.get("method", "text"),
            "added_at": now,
        }
        for chunk in new_chunks
    ]
    collection.add(
        ids=ids,
        documents=[chunk["text"] for chunk in new_chunks],
        embeddings=embeddings,
        metadatas=metadatas,
    )
    return len(new_chunks)

def search(query, top_k=10):
    collection = get_collection()
    if collection.count() == 0:
        return []
    results = collection.query(
        query_embeddings=[embed_texts([query])[0]],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )
    items = []
    for i, document in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        distance = results["distances"][0][i]
        items.append({
            "text": document,
            "source": metadata.get("source", "Unknown"),
            "page": metadata.get("page", 0),
            "method": metadata.get("method", "text"),
            "added_at": metadata.get("added_at", ""),
            "score": round(max(0.0, 1.0 - float(distance)), 4),
        })
    return items

def get_all_chunks(limit=40):
    collection = get_collection()
    if collection.count() == 0:
        return []
    result = collection.get(limit=min(limit, collection.count()), include=["documents", "metadatas"])
    return [
        {
            "text": result["documents"][i],
            "source": result["metadatas"][i].get("source", "Unknown"),
            "page": result["metadatas"][i].get("page", 0),
            "method": result["metadatas"][i].get("method", "text"),
        }
        for i in range(len(result["documents"]))
    ]

def get_documents():
    collection = get_collection()
    if collection.count() == 0:
        return []
    result = collection.get(include=["metadatas"])
    docs = {}
    for metadata in result["metadatas"]:
        source = metadata.get("source", "Unknown")
        entry = docs.setdefault(source, {"source": source, "chunks": 0, "pages": set(), "methods": set(), "added_at": metadata.get("added_at", "")})
        entry["chunks"] += 1
        page = metadata.get("page", 0)
        if page:
            entry["pages"].add(page)
        entry["methods"].add(metadata.get("method", "text"))
    return [
        {
            "source": value["source"],
            "chunks": value["chunks"],
            "pages": len(value["pages"]),
            "methods": ", ".join(sorted(value["methods"])),
            "added_at": value["added_at"],
        }
        for value in docs.values()
    ]

def delete_source(source):
    collection = get_collection()
    collection.delete(where={"source": source})

def get_stats():
    return {"chunks": get_collection().count(), "documents": len(get_documents())}
