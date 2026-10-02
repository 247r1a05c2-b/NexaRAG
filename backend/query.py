from __future__ import annotations

import os
from typing import Any

from .rag_engine import build_context, retrieve


def _fallback(question: str, context: str) -> dict[str, Any]:
    return {
        "answer": "I could not run the configured LLM. Please check GEMINI_API_KEY in the deployment environment.",
        "mode": "error",
        "sources": [],
        "retrieval": [],
    }


def _extract_sources(response: Any) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    try:
        metadata = response.candidates[0].grounding_metadata
        chunks = getattr(metadata, "grounding_chunks", None) or []
        for chunk in chunks:
            web = getattr(chunk, "web", None)
            if web:
                uri = getattr(web, "uri", None)
                title = getattr(web, "title", None)
                if uri and not any(x["url"] == uri for x in sources):
                    sources.append({"title": title or uri, "url": uri})
    except Exception:
        pass
    return sources


def answer_question(question: str, context: str = "") -> dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _fallback(question, context)
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        retrieved = retrieve(question, context, top_k=5) if context.strip() else []
        if context.strip() and retrieved:
            grounded_context = build_context(retrieved)
            prompt = f"""You are NexaRAG, a Retrieval-Augmented Generation assistant.
The RETRIEVED CONTEXT below is the only knowledge you may use to answer.
Synthesize an accurate answer from it. Do not invent facts. If the context is insufficient, explicitly state what is missing.
Mention the relevant source/chunk when useful.

RETRIEVED CONTEXT:
{grounded_context}

QUESTION:
{question}"""
            response = client.models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.1),
            )
            return {"answer": (response.text or "").strip(), "mode": "rag_llm", "sources": [], "retrieval": retrieved}

        if context.strip():
            return {
                "answer": "I searched the supplied data, but it does not contain enough relevant evidence to answer reliably. I have not substituted unrelated knowledge.",
                "mode": "rag_no_match",
                "sources": [],
                "retrieval": [],
            }

        prompt = f"""You are NexaRAG, a grounded research assistant.
No local data was supplied. Use the available web search tool to retrieve current, relevant evidence, then use the LLM to synthesize an answer.
Do not fabricate facts. Prefer authoritative sources and clearly state uncertainty.

QUESTION:
{question}"""
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2, tools=[types.Tool(google_search=types.GoogleSearch())]),
        )
        return {"answer": (response.text or "").strip(), "mode": "external_rag_llm", "sources": _extract_sources(response), "retrieval": []}
    except Exception as exc:
        result = _fallback(question, context)
        result["error"] = str(exc)[:300]
        return result
