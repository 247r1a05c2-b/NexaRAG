from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Any

_STORE = Path(os.getenv("NEXARAG_STORE", ".nexarag_store"))
_STORE.mkdir(parents=True, exist_ok=True)


def _chunks(text: str, size: int = 900, overlap: int = 120) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    out = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        out.append(text[start:end])
        if end == len(text):
            break
        start = max(start + 1, end - overlap)
    return out


def _tokens(s: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9_]{2,}", s.lower()))


def _score(query: str, text: str) -> float:
    q, t = _tokens(query), _tokens(text)
    if not q or not t:
        return 0.0
    return len(q & t) / len(q)


def ingest_text(text: str, source: str = "user-data") -> dict[str, Any]:
    chunks = _chunks(text)
    records = []
    for i, chunk in enumerate(chunks):
        records.append({"id": hashlib.sha256(f"{source}:{i}:{chunk}".encode()).hexdigest()[:16], "source": source, "chunk": i, "text": chunk})
    path = _STORE / "documents.jsonl"
    with path.open("a", encoding="utf-8") as f:
        import json
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return {"chunks_created": len(records), "source": source}


def retrieve(query: str, context: str = "", top_k: int = 5) -> list[dict[str, Any]]:
    candidates = []
    for i, chunk in enumerate(_chunks(context)):
        candidates.append({"id": f"request-{i}", "source": "user-data", "chunk": i, "text": chunk})
    path = _STORE / "documents.jsonl"
    if path.exists():
        import json
        with path.open(encoding="utf-8") as f:
            candidates.extend(json.loads(line) for line in f if line.strip())
    ranked = sorted(candidates, key=lambda x: _score(query, x["text"]), reverse=True)
    return [dict(x, score=round(_score(query, x["text"]), 4)) for x in ranked[:top_k] if _score(query, x["text"]) > 0]


def build_context(records: list[dict[str, Any]]) -> str:
    return "\n\n".join(f"[Source: {r['source']} | chunk {r['chunk']} | relevance {r['score']}]\n{r['text']}" for r in records)
