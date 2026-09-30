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
    if changed:
        report = scan_knowledge_health()
        print(f"health={report['health_score']} issues={len(report['issues'])}")
    return changed


def main():
    inbox = Path(os.getenv("KNOWLEDGE_INBOX", "knowledge_inbox"))
    interval = max(10, int(os.getenv("INGEST_INTERVAL_SECONDS", "60")))
    inbox.mkdir(parents=True, exist_ok=True)
    state = {}
    print(f"Watching {inbox.resolve()} every {interval}s")
    while True:
        try:
            run_once(inbox, state)
        except Exception as exc:
            print(f"worker_error={exc}")
        time.sleep(interval)


if __name__ == "__main__":
    main()
