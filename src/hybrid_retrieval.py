import re
from collections import Counter

def tokenize(text):
    return re.findall(r"[a-zA-Z0-9]+", text.lower())

def lexical_score(query, document):
    q = Counter(tokenize(query))
    d = Counter(tokenize(document))
    if not q or not d:
        return 0.0
    overlap = sum(min(q[token], d[token]) for token in q)
    return overlap / max(1, sum(q.values()))

def combine_scores(results, query):
    scored = []
    for rank, item in enumerate(results):
        semantic = float(item.get("score", 0.0))
        lexical = lexical_score(query, item["text"])
        rank_bonus = 1.0 / (rank + 1)
        item = dict(item)
        item["semantic_score"] = round(semantic, 4)
        item["lexical_score"] = round(lexical, 4)
        item["rank_score"] = round(rank_bonus, 4)
        item["hybrid_score"] = round((0.70 * semantic) + (0.20 * lexical) + (0.10 * rank_bonus), 4)
        scored.append(item)

    scored.sort(key=lambda x: x["hybrid_score"], reverse=True)

    selected = []
    seen_sources = set()
    for item in scored:
        source = item.get("source", "Unknown")
        if len(selected) < 3 or source not in seen_sources:
            selected.append(item)
            seen_sources.add(source)

    for item in scored:
        if item not in selected:
            selected.append(item)

    return selected
