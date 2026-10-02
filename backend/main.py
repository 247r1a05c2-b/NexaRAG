from __future__ import annotations
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel, Field
from .agents import IncidentCommander
from .llm_agent import generate_incident_summary
from .models import EventIn, IncidentCreate
from .query import answer_question
from .store import add_event, create_incident, get_incident, list_incidents, replace_incident

BASE = Path(__file__).resolve().parent.parent
app = FastAPI(title="NexaRAG Multi-Agent Incident Commander", version="2.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=BASE / "frontend"), name="static")
commander = IncidentCommander()

class QueryIn(BaseModel):
    question: str = Field(min_length=1, max_length=10000)
    context: str = Field(default="", max_length=100000)

@app.get("/", include_in_schema=False)
def root():
    return FileResponse(BASE / "frontend" / "index.html")

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "nexarag", "version": app.version}

@app.post("/api/query")
def query(data: QueryIn):
    return answer_question(data.question, data.context)

@app.get("/api/incidents")
def incidents():
    return list_incidents()

@app.post("/api/incidents")
def new_incident(data: IncidentCreate):
    return create_incident(data)

@app.get("/api/incidents/{incident_id}")
def incident(incident_id: str):
    item = get_incident(incident_id)
    if not item:
        raise HTTPException(404, "Incident not found")
    return item

@app.post("/api/incidents/{incident_id}/events")
def ingest(incident_id: str, event: EventIn):
    try:
        return add_event(incident_id, event)
    except KeyError:
        raise HTTPException(404, "Incident not found")

@app.post("/api/incidents/{incident_id}/analyze")
def analyze(incident_id: str):
    item = get_incident(incident_id)
    if not item:
        raise HTTPException(404, "Incident not found")
    commander.analyze(item)
    item.summary = generate_incident_summary(item.title, [e.model_dump() for e in item.events], item.hypotheses)
    return replace_incident(item)

@app.post("/api/incidents/{incident_id}/proposals/{proposal_index}/approve")
def approve(incident_id: str, proposal_index: int):
    item = get_incident(incident_id)
    if not item:
        raise HTTPException(404, "Incident not found")
    try:
        commander.approve(item, proposal_index)
    except (IndexError, ValueError) as exc:
        raise HTTPException(409, str(exc))
    return replace_incident(item)

@app.post("/api/demo/seed")
def seed_demo():
    incident = create_incident(IncidentCreate(title="Checkout API degradation", description="5xx spike and elevated latency after a deployment."))
    events = [
        EventIn(source_type="deployment", service="checkout", timestamp="2026-09-30T06:55:00Z", message="checkout-api v2.8.1 deployed to production", severity="info"),
        EventIn(source_type="log", service="checkout", timestamp="2026-09-30T06:57:10Z", message="POST /checkout returned 500: database connection timeout", severity="error"),
        EventIn(source_type="metric", service="checkout", timestamp="2026-09-30T06:58:00Z", message="p95 latency 4.8s, timeout rate 12%", severity="warning"),
        EventIn(source_type="alert", service="checkout", timestamp="2026-09-30T06:59:00Z", message="5xx error rate exceeded 10% threshold", severity="critical"),
        EventIn(source_type="ticket", service="checkout", timestamp="2026-09-30T07:01:00Z", message="Support reports customers unable to complete checkout", severity="high"),
        EventIn(source_type="chat", service="checkout", timestamp="2026-09-30T07:02:00Z", message="On-call notes DB connection pool saturation; no production changes approved yet", severity="info"),
    ]
    for event in events:
        add_event(incident.id, event)
    commander.analyze(incident)
    incident.summary = generate_incident_summary(incident.title, [e.model_dump() for e in incident.events], incident.hypotheses)
    return replace_incident(incident)
