from __future__ import annotations
from collections import Counter, defaultdict
from datetime import timedelta
import os
from typing import Any
from .models import EventIn, Incident, Proposal

DANGEROUS = ("rm ", "delete ", "drop ", "shutdown", "reboot", "kill ", "kubectl delete", "terraform destroy", "format ", "truncate ")

class IngestionAgent:
    name = "Ingestion Agent"
    def normalize(self, events: list[EventIn]) -> list[EventIn]:
        normalized = []
        for e in events:
            e.message = " ".join(e.message.split())
            e.service = e.service.strip().lower() or "unknown"
            e.severity = e.severity.lower()
            normalized.append(e)
        return sorted(normalized, key=lambda e: e.timestamp or 0)

class CorrelationAgent:
    name = "Correlation Agent"
    def correlate(self, events: list[EventIn]) -> dict[str, Any]:
        by_service: dict[str, list[EventIn]] = defaultdict(list)
        for event in events:
            by_service[event.service].append(event)
        signal_counts = Counter()
        for e in events:
            text = e.message.lower()
            for key in ("timeout", "5xx", "error", "latency", "oom", "connection", "deploy", "auth"):
                if key in text:
                    signal_counts[key] += 1
        return {"services": {k: len(v) for k, v in by_service.items()}, "signals": dict(signal_counts), "event_count": len(events)}

class RootCauseAgent:
    name = "Root Cause Agent"
    def diagnose(self, incident: Incident, correlation: dict[str, Any]) -> list[dict[str, Any]]:
        text = " ".join(e.message.lower() for e in incident.events)
        deployments = [e for e in incident.events if e.source_type == "deployment"]
        errors = [e for e in incident.events if any(k in e.message.lower() for k in ("error", "5xx", "timeout", "oom"))]
        hypotheses = []
        if deployments and errors:
            hypotheses.append({"cause": "Recent deployment regression", "confidence": 0.91, "evidence": f"{len(deployments)} deployment event(s) precede {len(errors)} error signal(s)."})
        if "connection" in text or "database" in text or "db" in text:
            hypotheses.append({"cause": "Database connection or saturation issue", "confidence": 0.84, "evidence": "Connection/database failure signals appear in incident telemetry."})
        if "latency" in text or "timeout" in text:
            hypotheses.append({"cause": "Upstream latency or timeout cascade", "confidence": 0.78, "evidence": "Latency/timeout signals are present across incident events."})
        if "oom" in text or "memory" in text:
            hypotheses.append({"cause": "Memory pressure", "confidence": 0.86, "evidence": "Memory/OOM signals are present in telemetry."})
        if "auth" in text or "unauthorized" in text:
            hypotheses.append({"cause": "Authentication or credential failure", "confidence": 0.73, "evidence": "Authentication failure signals are present."})
        if not hypotheses:
            hypotheses.append({"cause": "Insufficient correlated evidence", "confidence": 0.42, "evidence": "No deterministic failure pattern crossed the diagnostic threshold."})
        return sorted(hypotheses, key=lambda x: x["confidence"], reverse=True)

class SafetyAgent:
    name = "Safety & Guardrail Agent"
    def propose(self, hypotheses: list[dict[str, Any]]) -> list[Proposal]:
        proposals: list[Proposal] = []
        for h in hypotheses[:3]:
            cause = h["cause"]
            if "deployment" in cause.lower():
                action = "Compare the current deployment with the previous known-good version and run read-only health checks."
                verify = "Confirm error rate and latency return toward baseline before any rollback decision."
            elif "database" in cause.lower():
                action = "Inspect read-only database connection counts, latency, saturation and recent configuration changes."
                verify = "Confirm database metrics stabilize without changing production state."
            elif "latency" in cause.lower():
                action = "Run read-only upstream latency and dependency health checks for the affected service."
                verify = "Confirm p95 latency and timeout rate against the pre-incident baseline."
            elif "memory" in cause.lower():
                action = "Inspect memory utilization, container limits and recent allocation trends without changing workloads."
                verify = "Confirm memory pressure is decreasing and no new OOM events occur."
            else:
                action = "Collect additional read-only logs, metrics and deployment metadata before taking action."
                verify = "Require an evidence threshold before changing live infrastructure."
            proposals.append(Proposal(action=action, rationale=f"Supports hypothesis: {cause} ({h['confidence']:.0%}).", risk="low", safe_to_execute=False, requires_human=True, verification=verify))
        return proposals

class TimelineAgent:
    name = "Timeline Agent"
    def build(self, incident: Incident) -> list[dict[str, Any]]:
        timeline = []
        for e in sorted(incident.events, key=lambda x: x.timestamp or 0):
            timeline.append({"timestamp": e.timestamp.isoformat() if e.timestamp else None, "source": e.source_type, "service": e.service, "severity": e.severity, "message": e.message})
        return timeline

class IncidentCommander:
    def __init__(self) -> None:
        self.ingestion = IngestionAgent()
        self.correlation = CorrelationAgent()
        self.root_cause = RootCauseAgent()
        self.safety = SafetyAgent()
        self.timeline = TimelineAgent()

    def analyze(self, incident: Incident) -> Incident:
        incident.events = self.ingestion.normalize(incident.events)
        correlation = self.correlation.correlate(incident.events)
        incident.hypotheses = self.root_cause.diagnose(incident, correlation)
        incident.proposals = self.safety.propose(incident.hypotheses)
        incident.timeline = self.timeline.build(incident)
        top = incident.hypotheses[0]
        incident.summary = f"Most probable cause: {top['cause']} ({top['confidence']:.0%}). {top['evidence']} No autonomous production command is executed."
        return incident

    def approve(self, incident: Incident, index: int) -> Incident:
        if index < 0 or index >= len(incident.proposals):
            raise IndexError(index)
        proposal = incident.proposals[index]
        if proposal.risk != "low" or not proposal.safe_to_execute:
            raise ValueError("Production execution is blocked by the safety policy; only human-reviewed, read-only proposals are allowed.")
        proposal.status = "approved"
        return incident


def validate_command(command: str) -> bool:
    normalized = command.lower().strip()
    return not any(token in normalized for token in DANGEROUS)
