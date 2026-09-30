import json
import re
from datetime import datetime, timezone

from src.llm import generate_text
from src.vector_store import get_all_chunks, set_chunk_status


def _extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {"issues": []}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"issues": []}


def scan_knowledge_base(limit=60):
    chunks = get_all_chunks(limit=limit)
    if not chunks:
        return {"status": "empty", "health_score": 0, "issues": [], "checked_chunks": 0, "checked_at": datetime.now(timezone.utc).isoformat()}

    evidence = []
    for index, chunk in enumerate(chunks):
        evidence.append(
            f"CHUNK {index}\nID: {chunk['id']}\nSOURCE: {chunk['source']}\n"
            f"PAGE: {chunk['page']}\nADDED_AT: {chunk.get('added_at', '')}\n"
            f"STATUS: {chunk.get('status', 'active')}\nTEXT: {chunk['text']}"
        )

    prompt = """You are the Knowledge Integrity Agent for NexaRAG.
Inspect the supplied knowledge chunks and find only evidence-based integrity problems.
Look for direct factual contradictions, a newer chunk that clearly supersedes an older conflicting chunk, duplicated claims that could create retrieval ambiguity, and weak or incomplete evidence.
Do not invent facts. Do not call two statements a conflict merely because they have different scopes or dates.
Return ONLY valid JSON:
{"issues":[{"type":"conflict|duplicate|weak_evidence","chunk_ids":["id1","id2"],"preferred_chunk_id":"id1 or null","confidence":0.0,"reason":"short evidence-based explanation","repair":"quarantine_old|keep_both|review"}]}
Only include issues with confidence >= 0.75. Prefer quarantine_old only when the evidence clearly indicates that one chunk supersedes another.

KNOWLEDGE CHUNKS:
""" + "\n\n".join(evidence)

    report = _extract_json(generate_text(prompt))
    issues = report.get("issues", []) if isinstance(report, dict) else []
    valid_ids = {chunk["id"] for chunk in chunks}
    cleaned = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        ids = [item for item in issue.get("chunk_ids", []) if item in valid_ids]
        try:
            confidence = float(issue.get("confidence", 0) or 0)
        except (TypeError, ValueError):
            confidence = 0
        if len(ids) < 2 or confidence < 0.75:
            continue
        issue["chunk_ids"] = ids
        issue["confidence"] = round(confidence, 2)
        cleaned.append(issue)

    conflict_count = sum(1 for item in cleaned if item.get("type") == "conflict")
    duplicate_count = sum(1 for item in cleaned if item.get("type") == "duplicate")
    weak_count = sum(1 for item in cleaned if item.get("type") == "weak_evidence")
    health_score = max(0, 100 - conflict_count * 20 - duplicate_count * 8 - weak_count * 5)
    return {
        "status": "healthy" if health_score >= 85 else "needs_repair",
        "health_score": health_score,
        "issues": cleaned,
        "checked_chunks": len(chunks),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def heal_knowledge_base(report):
    repaired = []
    skipped = []
    for issue in report.get("issues", []):
        if issue.get("repair") != "quarantine_old" or not issue.get("preferred_chunk_id"):
            skipped.append(issue)
            continue
        preferred = issue["preferred_chunk_id"]
        for chunk_id in issue.get("chunk_ids", []):
            if chunk_id == preferred:
                continue
            set_chunk_status(
                chunk_id,
                "quarantined",
                healing_reason=issue.get("reason", "Superseded conflicting evidence"),
                healed_at=datetime.now(timezone.utc).isoformat(),
            )
            repaired.append({"chunk_id": chunk_id, "kept_chunk_id": preferred, "reason": issue.get("reason", "Superseded conflicting evidence")})
    return {"repaired": repaired, "skipped": skipped, "repaired_count": len(repaired), "healed_at": datetime.now(timezone.utc).isoformat()}
