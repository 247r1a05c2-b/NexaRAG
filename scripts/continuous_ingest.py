import hashlib
import os
import time
from pathlib import Path

from src.document_loader import load_uploaded_file
from src.rag_pipeline import build_index, scan_knowledge_health

SUPPORTED = {".pdf", ".docx", ".pptx", ".txt", ".png", ".jpg", ".jpeg"}


class LocalUpload:
    def __init__(self, path: Path):
        self.name = path.name
        self._data = path.read_bytes()

    def getvalue(self):
        return self._data


def fingerprint(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_once(inbox: Path, state: dict):
    changed = 0
    for path in sorted(inbox.iterdir()):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED:
            continue
        digest = fingerprint(path)
        if state.get(path.name) == digest:
            continue
        documents = load_uploaded_file(LocalUpload(path))
        added = build_index(documents)
        state[path.name] = digest
        changed += added
        print(f"ingested={path.name} chunks={added}")
    return changed


def main():
    inbox = Path(os.getenv("KNOWLEDGE_INBOX", "knowledge_inbox"))
    interval = max(10, int(os.getenv("INGEST_INTERVAL_SECONDS", "60")))
    audit_interval = max(30, int(os.getenv("AUDIT_INTERVAL_SECONDS", "300")))
    inbox.mkdir(parents=True, exist_ok=True)
    state = {}
    last_audit = 0.0
    print(f"Watching {inbox.resolve()} every {interval}s; auditing every {audit_interval}s")
    while True:
        try:
            run_once(inbox, state)
            now = time.time()
            if now - last_audit >= audit_interval:
                report = scan_knowledge_health()
                print(f"health={report['health_score']} issues={len(report['issues'])} checked={report['checked_chunks']}")
                last_audit = now
        except Exception as exc:
            print(f"worker_error={exc}")
        time.sleep(interval)


if __name__ == "__main__":
    main()
