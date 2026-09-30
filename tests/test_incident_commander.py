from datetime import datetime, timezone
from fastapi.testclient import TestClient
from backend.agents import CorrelationAgent, IncidentCommander, validate_command
from backend.main import app
from backend.models import EventIn, Incident


def event(kind, message, service="checkout"):
    return EventIn(source_type=kind, service=service, timestamp=datetime.now(timezone.utc), message=message, severity="error")


def test_correlation_counts_operational_signals():
    result = CorrelationAgent().correlate([event("log", "500 error after timeout"), event("metric", "latency increased")])
    assert result["event_count"] == 2
    assert result["signals"]["error"] >= 1
    assert result["signals"]["timeout"] >= 1


def test_commander_detects_deployment_regression_and_safe_proposal():
    incident = Incident(id="INC-1", title="API outage", description="", created_at=datetime.now(timezone.utc), events=[
        event("deployment", "v2.8.1 deployed"), event("log", "500 error: database connection timeout"), event("alert", "5xx error rate high")
    ])
    result = IncidentCommander().analyze(incident)
    assert result.hypotheses[0]["cause"] == "Recent deployment regression"
    assert result.hypotheses[0]["confidence"] > 0.9
    assert result.proposals[0].requires_human is True
    assert result.proposals[0].safe_to_execute is False
    assert len(result.timeline) == 3


def test_dangerous_commands_are_blocked():
    assert validate_command("kubectl get pods") is True
    assert validate_command("kubectl delete deployment checkout") is False
    assert validate_command("rm -rf /") is False


def test_api_demo_and_analysis_flow():
    client = TestClient(app)
    seeded = client.post("/api/demo/seed")
    assert seeded.status_code == 200
    incident = seeded.json()
    assert incident["hypotheses"]
    assert incident["timeline"]
    response = client.get("/api/incidents/" + incident["id"])
    assert response.status_code == 200
    assert response.json()["events"]


def test_api_rejects_unknown_incident():
    client = TestClient(app)
    response = client.post("/api/incidents/INC-NOPE/analyze")
    assert response.status_code == 404
