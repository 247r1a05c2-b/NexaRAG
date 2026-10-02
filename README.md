# 🚀 NexaRAG — Grounded Knowledge Assistant + Multi-Agent Incident Commander

NexaRAG now has two connected capabilities: a **data-first Q&A engine** and a **multi-agent incident commander**.

## 1. Data-first Q&A

Open the app and use **Knowledge Q&A**.

- Enter a question.
- Paste any data you have: logs, notes, JSON, reports, tables, tickets, documents or plain text.
- NexaRAG answers using the supplied data first and does not intentionally add outside facts.
- If the data box is empty, NexaRAG automatically switches to **grounded external search** through Gemini's web-search grounding.
- Returned external sources are displayed under the answer when the provider exposes them.
- If the model cannot retrieve reliable evidence, it says so instead of pretending it knows.

### Example

```text
Question: What caused the outage?
Data: checkout deployed v2.8.1 at 06:55; DB connection timeouts started at 06:57; 5xx reached 12% at 06:59.
```

The answer is grounded in those supplied facts.

If the Data / context box is empty:

```text
Question: What is the latest stable Python release?
```

NexaRAG uses external search and provides the answer with available sources.

## 2. Multi-agent incident commander

The existing incident workspace remains available for operational diagnosis:

| Agent | Responsibility |
|---|---|
| Ingestion Agent | Normalizes incident events |
| Correlation Agent | Links signals by service and failure pattern |
| Root Cause Agent | Produces evidence-ranked hypotheses |
| Safety & Guardrail Agent | Keeps proposed diagnostics read-only |
| Timeline Agent | Builds an auditable incident timeline |
| Commander | Orchestrates the analysis |
| Gemini Copilot | Optional grounded executive summary |

The commander is advisory by design. It does not execute shell, Kubernetes, cloud, database mutation, rollback or destructive commands.

## Run locally

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Open `http://localhost:8000`.

## Gemini configuration

Create a `.env` file or set environment variables:

```text
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-2.5-flash
```

The incident commander still has deterministic fallback behavior when Gemini is unavailable. The Q&A endpoint requires Gemini for external web retrieval.

## API

### Grounded Q&A

`POST /api/query`

```json
{
  "question": "What caused the error?",
  "context": "Paste your evidence here"
}
```

Behavior:

```text
User question + supplied data
          |
          v
     Data available?
       /        \
     YES         NO
      |           |
      v           v
Answer only   Grounded web
from data      retrieval
      |           |
      +-----+-----+
            v
     Evidence-backed answer
```

### Incident APIs

- `GET /api/health`
- `GET /api/incidents`
- `POST /api/incidents`
- `GET /api/incidents/{id}`
- `POST /api/incidents/{id}/events`
- `POST /api/incidents/{id}/analyze`
- `POST /api/incidents/{id}/proposals/{index}/approve`
- `POST /api/demo/seed`

## Tests

```bash
python -m compileall backend tests
PYTHONPATH=. pytest -q
```

## Deployment

The repository contains Docker support and GitHub Actions CI. For a hosted deployment, configure `GEMINI_API_KEY` as a server-side environment variable; never put the key in frontend JavaScript.
