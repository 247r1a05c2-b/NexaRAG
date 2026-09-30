from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import chromadb

AUDIT_COLLECTION = "nexarag_audit"
_client = chromadb.PersistentClient(path="data/chroma")


def _collection():
    return _client.get_or_create_collection(name=AUDIT_COLLECTION)


def record_event(event_type: str, payload: dict[str, Any]):
    timestamp = datetime.now(timezone.utc).isoformat()
    event_id = f"event-{timestamp}-{uuid4().hex}"
    _collection().add(ids=[event_id], documents=[repr(payload)], metadatas=[{"event_type": event_type, "timestamp": timestamp}])
    return event_id


def list_events(limit: int = 50):
    collection = _collection()
    if collection.count() == 0:
        return []
    result = collection.get(limit=min(limit, collection.count()), include=["documents", "metadatas"])
    return [{"event": result["metadatas"][i].get("event_type", "unknown"), "timestamp": result["metadatas"][i].get("timestamp", ""), "details": result["documents"][i]} for i in range(len(result["documents"]))]
