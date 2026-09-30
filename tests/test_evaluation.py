from src.evaluation import evaluate_integrity_report, evaluate_retrieval_case


def test_retrieval_evaluation_metrics():
    results = [
        {"source": "a.pdf", "score": 0.9},
        {"source": "b.pdf", "score": 0.8},
        {"source": "noise.pdf", "score": 0.1},
    ]
    metrics = evaluate_retrieval_case(results, ["a.pdf", "b.pdf"])
    assert metrics["source_recall"] == 1.0
    assert metrics["source_precision"] == 1.0
    assert metrics["source_f1"] == 1.0


def test_integrity_evaluation_metrics():
    report = {
        "health_score": 80,
        "checked_chunks": 10,
        "issues": [
            {"repair": "quarantine_old"},
            {"repair": "review"},
        ],
    }
    assert evaluate_integrity_report(report) == {
        "health_score": 80,
        "issues": 2,
        "auto_healable": 1,
        "human_review": 1,
        "checked_chunks": 10,
    }
