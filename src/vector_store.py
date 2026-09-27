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
        {
            "source": chunk["source"],
            "page": chunk["page"] if chunk["page"] is not None else 0,
        }
        for chunk in chunks
    ]
    collection.add(
        ids=ids,
        documents=[chunk["text"] for chunk in chunks],
        embeddings=embeddings,
        metadatas=metadatas,
    )
    return len(chunks)

def search(query, top_k=5):
    collection = get_collection()
    if collection.count() == 0:
        return []
    results = collection.query(
        query_embeddings=[embed_texts([query])[0]],
        n_results=min(top_k, collection.count()),
    )
    items = []
    for i, document in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        items.append({
            "text": document,
            "source": metadata.get("source", "Unknown"),
            "page": metadata.get("page", 0),
        })
    return items
