from __future__ import annotations
from threading import RLock
from uuid import uuid4
from .models import Incident, IncidentCreate, EventIn, now

_lock = RLock()
_incidents: dict[str, Incident] = {}


def create_incident(data: IncidentCreate) -> Incident:
    incident = Incident(id=f"INC-{uuid4().hex[:8].upper()}", title=data.title, description=data.description, created_at=now())
    with _lock:
        _incidents[incident.id] = incident
    return incident


def get_incident(incident_id: str) -> Incident | None:
    with _lock:
        return _incidents.get(incident_id)


def list_incidents() -> list[Incident]:
    with _lock:
        return sorted(_incidents.values(), key=lambda x: x.created_at, reverse=True)


def add_event(incident_id: str, event: EventIn) -> Incident:
    incident = get_incident(incident_id)
    if not incident:
        raise KeyError(incident_id)
    if event.timestamp is None:
        event.timestamp = now()
    incident.events.append(event)
    return incident


def replace_incident(incident: Incident) -> Incident:
    with _lock:
        _incidents[incident.id] = incident
    return incident


def clear() -> None:
    with _lock:
        _incidents.clear()
