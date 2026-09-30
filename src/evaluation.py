def retrieval_quality(results, minimum_score=0.35):
    if not results:
        return {"retrieved": 0, "useful": 0, "coverage": 0.0}
    useful = sum(1 for item in results if item.get("hybrid_score", item.get("score", 0)) >= minimum_score)
    return {"retrieved": len(results), "useful": useful, "coverage": round(useful / len(results), 2)}


def build_test_questions():
    return [
        "What is the main purpose of the document?",
        "What are the most important requirements?",
        "What risks or limitations are mentioned?",
        "What actions or recommendations are given?",
        "What key facts should a decision maker know?",
    ]


def answer_quality_label(retrieval):
    coverage = retrieval.get("coverage", 0.0)
    if coverage >= 0.75:
        return "High retrieval support"
    if coverage >= 0.45:
        return "Moderate retrieval support"
    return "Low retrieval support"


def evaluate_retrieval_case(results, expected_sources, minimum_score=0.35):
    expected = {str(source) for source in expected_sources}
    retrieved_sources = {str(item.get("source", "")) for item in results if item.get("hybrid_score", item.get("score", 0)) >= minimum_score}
    hit_count = len(expected & retrieved_sources)
    recall = hit_count / len(expected) if expected else 1.0
    precision = hit_count / len(retrieved_sources) if retrieved_sources else 0.0
    f1 = 0.0 if recall + precision == 0 else 2 * recall * precision / (recall + precision)
    return {"source_recall": round(recall, 3), "source_precision": round(precision, 3), "source_f1": round(f1, 3)}


def evaluate_integrity_report(report):
    issues = report.get("issues", [])
    auto_healed = sum(issue.get("repair") == "quarantine_old" for issue in issues)
    review = sum(issue.get("repair") == "review" for issue in issues)
    return {
        "health_score": report.get("health_score", 0),
        "issues": len(issues),
        "auto_healable": auto_healed,
        "human_review": review,
        "checked_chunks": report.get("checked_chunks", 0),
    }
