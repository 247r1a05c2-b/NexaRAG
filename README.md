# 🚨 NexaRAG Command — Multi-Agent Incident Commander

**NRCM PNG2 · Generative AI & LLM Applications**

NexaRAG Command is a production-safe, multi-agent incident response system that ingests noisy operational signals, correlates evidence, ranks probable root causes, builds an auditable incident timeline, and proposes safe diagnostic steps for human engineers.

## Problem
During outages, engineers face fragmented logs, alerts, tickets, deployment history and chat messages. NexaRAG Command turns these streams into one evidence-backed incident view without allowing an LLM to execute unsafe production actions.

## Core agents

| Agent | Responsibility |
|---|---|
| Ingestion Agent | Normalizes heterogeneous incident events |
| Correlation Agent | Links signals by service and failure pattern |
| Root Cause Agent | Ranks probable failure causes with confidence |
| Safety & Guardrail Agent | Generates read-only diagnostic proposals and blocks unsafe actions |
| Timeline Agent | Builds a chronological, auditable incident timeline |
| Commander | Orchestrates the agents and produces the incident brief |
| Optional Gemini Copilot | Converts evidence into a concise executive summary |

## Architecture

```text
Logs ───────┐
Alerts ─────┤
Tickets ────┤
Deployments ┼──> Ingestion ─> Correlation ─> Root Cause ─> Safety Guardrail
Chat ───────┤                                      │             │
Metrics ────┘                                      └──────┬──────┘
                                                        ↓
                                             Timeline + Commander UI
                                                        ↓
                                                Human verification
```

## Safety model
The commander is **advisory by design**. It does not execute shell, Kubernetes, cloud, database mutation, rollback or destructive commands. Diagnostic proposals are read-only and require human verification. Dangerous command patterns are explicitly blocked and covered by tests.

## Features
- Multi-agent incident analysis
- Logs, alerts, tickets, deployments, chat and metrics ingestion
- Evidence correlation across services
- Ranked root-cause hypotheses
- Confidence scoring
- Safe diagnostic proposals
- Human-in-the-loop approval state
- Auditable chronological timeline
- Production-safe guardrails
- Optional Gemini LLM executive summary
- Built-in realistic outage demo
- Responsive frontend dashboard
- FastAPI backend
- Docker deployment
- Automated GitHub Actions CI
- Deterministic fallback mode when no API key is available
- Full unit/API test suite

## Demo
Click **Load Demo Incident**. The system creates a checkout degradation where a deployment is followed by database connection timeouts, elevated p95 latency and 5xx alerts.

Expected flow:

```text
Incident
   ↓
6 heterogeneous events
   ↓
5 agents collaborate
   ↓
Deployment regression ranked with high confidence
   ↓
Read-only diagnostic proposals
   ↓
Human verification required
   ↓
Auditable timeline
```

## Run locally

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# Linux/macOS
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Open **http://localhost:8000**.

Optional Gemini:

```text
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-2.5-flash
```

The project works without Gemini using deterministic analysis, which keeps demos and tests reproducible.

## Tests

```bash
python -m compileall backend tests
pytest -q
```

Tests cover:
- Event correlation
- Root-cause diagnosis
- Safety gating
- Dangerous-command blocking
- End-to-end demo API flow
- Unknown incident handling

## Deployment

```bash
docker build -t nexarag-command .
docker run -p 8000:8000 nexarag-command
```

Kubernetes manifests can be added on top of the container for production scaling and monitoring.

## Existing NexaRAG work
The original document RAG/knowledge-base implementation remains in the repository as reusable infrastructure. The PNG2 commander is the new primary hackathon application and can later connect to that RAG layer for runbook retrieval and historical incident knowledge.
