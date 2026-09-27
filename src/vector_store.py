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
    embeddings = embed_texts([chunk["text"] for chunk in chunks])
    ids = [f"chunk-{i}" for i in range(len(chunks))]
    metadatas = [
        {"source": chunk["source"], "page": chunk["page"] if chunk["page"] is not None else 0}
        for chunk in chunks
    ]
    collection.add(
        ids=ids,
        documents=[chunk["text"] for chunk in chunks],
        embeddings=embeddings,
        metadatas=metadatas,
    )
    return len(chunks)

def search(query, top_k=8):
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
            "score": round(max(0.0, 1.0 - float(distance)), 4),
        })
    return items

def get_all_chunks(limit=30):
    collection = get_collection()
    if collection.count() == 0:
        return []
    result = collection.get(limit=min(limit, collection.count()), include=["documents", "metadatas"])
    return [
        {
            "text": result["documents"][i],
            "source": result["metadatas"][i].get("source", "Unknown"),
            "page": result["metadatas"][i].get("page", 0),
        }
        for i in range(len(result["documents"]))
    ]

def get_stats():
    return {"chunks": get_collection().count()}
