from __future__ import annotations
import os
from typing import Any


def generate_incident_summary(incident_title: str, events: list[dict[str, Any]], hypotheses: list[dict[str, Any]]) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        if hypotheses:
            top = hypotheses[0]
            return f"{incident_title}: evidence currently points to {top['cause']} ({top['confidence']:.0%}). The commander recommends read-only verification before any production change."
        return f"{incident_title}: insufficient evidence for a safe root-cause conclusion."
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        prompt = (
            "You are a production incident analysis assistant. Summarize only the supplied evidence. "
            "Never invent facts and never recommend destructive or autonomous production actions. "
            f"Incident: {incident_title}\nEvents: {events}\nHypotheses: {hypotheses}\n"
            "Return a concise executive summary with cause, evidence, uncertainty and safe next step."
        )
        response = client.models.generate_content(model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), contents=prompt)
        return response.text.strip()
    except Exception:
        return generate_incident_summary.__wrapped__(incident_title, events, hypotheses) if hasattr(generate_incident_summary, "__wrapped__") else (f"{incident_title}: LLM unavailable; deterministic evidence points to {hypotheses[0]['cause']} ({hypotheses[0]['confidence']:.0%})." if hypotheses else "Insufficient evidence.")
