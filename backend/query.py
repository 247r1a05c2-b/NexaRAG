from __future__ import annotations

import os
from typing import Any


def _fallback(question: str, context: str) -> dict[str, Any]:
    if context.strip():
        return {
            "answer": "I could not run the configured LLM. Based only on the supplied data, I cannot safely produce a reliable answer. Please configure GEMINI_API_KEY.",
            "mode": "provided_data",
            "sources": [],
        }
    return {
        "answer": "No data was supplied and the external information provider is not configured. Set GEMINI_API_KEY to enable grounded web retrieval.",
        "mode": "external_search_unavailable",
        "sources": [],
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
        has_context = bool(context.strip())
        if has_context:
            prompt = f"""You are NexaRAG, an evidence-grounded question answering assistant.
Answer the user's question using ONLY the supplied data. Do not use outside knowledge and do not invent missing facts.
If the supplied data does not contain enough information, clearly say what is missing.
Return a concise, useful answer and mention the relevant facts from the data.

SUPPLIED DATA:
{context}

QUESTION:
{question}"""
            config = types.GenerateContentConfig(temperature=0.1)
            response = client.models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                contents=prompt,
                config=config,
            )
            return {
                "answer": (response.text or "").strip(),
                "mode": "provided_data",
                "sources": [],
            }

        prompt = f"""You are NexaRAG, a grounded research assistant.
No user data was supplied. Research the user's question using the available web search tool, then answer from the retrieved evidence.
Prefer authoritative and current sources. Do not fabricate facts. Clearly distinguish established facts from uncertainty.
Include useful source links when available.

QUESTION:
{question}"""
        config = types.GenerateContentConfig(
            temperature=0.2,
            tools=[types.Tool(google_search=types.GoogleSearch())],
        )
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt,
            config=config,
        )
        return {
            "answer": (response.text or "").strip(),
            "mode": "external_search",
            "sources": _extract_sources(response),
        }
    except Exception as exc:
        result = _fallback(question, context)
        result["error"] = str(exc)[:300]
        return result
