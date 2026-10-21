from backend.rag_engine import _chunks, _score, build_context


def test_chunks_returns_empty_for_blank_text():
    assert _chunks("   \n  ") == []


def test_chunks_normalizes_whitespace_and_preserves_content():
    chunks = _chunks("alpha   beta\n gamma", size=50, overlap=5)
    assert chunks == ["alpha beta gamma"]


def test_relevance_score_rewards_query_token_coverage():
    assert _score("database timeout", "database timeout after deploy") == 1.0
    assert _score("database timeout", "cache misses") == 0.0


def test_build_context_includes_source_and_text():
    context = build_context([{"source": "runbook.md", "chunk": 0, "score": 0.8, "text": "Restart worker"}])
    assert "runbook.md" in context
    assert "Restart worker" in context
