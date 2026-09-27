def retrieval_quality(results, minimum_score=0.35):
    if not results:
        return {
            "retrieved": 0,
            "useful": 0,
            "coverage": 0.0,
        }

    useful = sum(1 for item in results if item.get("hybrid_score", item.get("score", 0)) >= minimum_score)
    return {
        "retrieved": len(results),
        "useful": useful,
        "coverage": round(useful / len(results), 2),
    }

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
