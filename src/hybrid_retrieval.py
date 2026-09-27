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
    for item in results:
        semantic = float(item.get("score", 0.0))
        lexical = lexical_score(query, item["text"])
        item = dict(item)
        item["semantic_score"] = semantic
        item["lexical_score"] = round(lexical, 4)
        item["hybrid_score"] = round((0.75 * semantic) + (0.25 * lexical), 4)
        scored.append(item)
    return sorted(scored, key=lambda x: x["hybrid_score"], reverse=True)
