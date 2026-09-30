# PNG2 — Multi-Agent Incident Commander

## Mission
NexaRAG Command is an advisory AI incident commander. It ingests noisy operational signals, correlates evidence, ranks probable root causes, builds an auditable timeline, and proposes low-risk diagnostic steps for human engineers.

## Agent topology

```text
Logs ───────┐
Alerts ─────┤
Tickets ────┤
Deployments ┼──> Ingestion Agent ──> Correlation Agent ──> Root Cause Agent
Chat ───────┤                                              │
Metrics ────┘                                              v
                                           Safety / Guardrail Agent
                                                      │
                                                      v
                                           Timeline + Commander UI
                                                      │
                                                      v
                                           Human verification
```

## Production safety
- The system is advisory by design.
- No shell, cloud, Kubernetes, database mutation or rollback command is executed by the agents.
- Diagnostic proposals are read-only and require human verification.
- Dangerous command patterns are blocked by policy tests.
- LLM output is treated as untrusted analysis and is bounded by deterministic safety rules.

## Evaluation
The test suite covers event correlation, deployment-regression diagnosis, safety gating, dangerous-command blocking, demo end-to-end API flow, and unknown-incident handling.

## Demo scenario
The built-in demo creates a checkout degradation where a deployment is followed by database connection timeouts, high p95 latency and 5xx alerts. The agents should rank a deployment regression as the top hypothesis and produce read-only diagnostic proposals.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Open `http://localhost:8000`.

Optional Gemini enhancement:

```bash
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-2.5-flash
```

Without an API key, deterministic incident analysis still works, so the demo and tests remain reproducible.
