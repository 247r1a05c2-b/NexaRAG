"""Offline tests for NexaRAG query behavior."""

from backend.query import answer_question


def test_missing_api_key_returns_explicit_error(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    result = answer_question("What caused the incident?", "timeouts after deployment")

    assert result["mode"] == "error"
    assert result["sources"] == []
    assert result["retrieval"] == []
    assert "GEMINI_API_KEY" in result["answer"]


def test_empty_question_does_not_require_external_service(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    result = answer_question("", "")

    assert result["mode"] == "error"
    assert isinstance(result["answer"], str)
    assert result["answer"]
