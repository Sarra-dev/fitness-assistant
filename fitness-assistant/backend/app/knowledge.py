"""Tiny retrieval engine (TF-IDF + cosine similarity, pure Python).

It indexes the exercises and nutrition tips, and returns the entries most relevant
to a user question. Those entries are given to the LLM as context (RAG) and are
also returned to the frontend as `sources`.
"""
import json
import math
import re
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "to", "in", "on", "for", "with", "is", "are",
    "i", "me", "my", "you", "your", "it", "this", "that", "can", "do", "does", "how",
    "what", "which", "want", "need", "please", "give", "some", "be", "have", "get",
    "should", "would", "could", "at", "as", "by", "from", "about", "am", "we",
}


def tokenize(text: str) -> list[str]:
    tokens = []
    for tok in re.findall(r"[a-z0-9]+", text.lower()):
        if tok in STOPWORDS or len(tok) < 2:
            continue
        if len(tok) > 3 and tok.endswith("s"):  # very light stemming: legs -> leg
            tok = tok[:-1]
        tokens.append(tok)
    return tokens


class KnowledgeBase:
    def __init__(self) -> None:
        self.exercises: list[dict] = json.loads(
            (DATA_DIR / "exercises.json").read_text(encoding="utf-8")
        )
        tips = json.loads((DATA_DIR / "nutrition.json").read_text(encoding="utf-8"))

        self.docs: list[dict] = []
        for e in self.exercises:
            self.docs.append(
                {
                    "title": e["title"],
                    "category": e["category"],
                    "kind": "exercise",
                    "text": f'{e["title"]}. {e["description"]} '
                    f'Muscles: {", ".join(e["muscles"])}. Level: {e["level"]}.',
                }
            )
        for t in tips:
            self.docs.append(
                {
                    "title": t["title"],
                    "category": "Nutrition",
                    "kind": "nutrition",
                    "text": f'{t["title"]}. {t["content"]}',
                }
            )
        self._build_index()

    # -- indexing ---------------------------------------------------------
    def _build_index(self) -> None:
        doc_tokens = [tokenize(d["text"] + " " + d["category"]) for d in self.docs]
        n = len(self.docs)
        df: Counter = Counter()
        for toks in doc_tokens:
            df.update(set(toks))
        self.idf = {t: math.log((1 + n) / (1 + c)) + 1 for t, c in df.items()}
        self.vectors = [self._vectorize(toks) for toks in doc_tokens]

    def _vectorize(self, tokens: list[str]) -> dict[str, float]:
        tf = Counter(tokens)
        vec = {
            t: (1 + math.log(c)) * self.idf[t] for t, c in tf.items() if t in self.idf
        }
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {t: v / norm for t, v in vec.items()}

    # -- querying ---------------------------------------------------------
    def search(self, query: str, k: int = 4) -> list[dict]:
        q = self._vectorize(tokenize(query))
        if not q:
            return []
        scored = []
        for doc, vec in zip(self.docs, self.vectors):
            score = sum(w * vec.get(t, 0.0) for t, w in q.items())
            if score > 0.05:
                scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:k]]

    def list_exercises(self, category: str | None = None) -> list[dict]:
        if not category:
            return self.exercises
        return [e for e in self.exercises if e["category"].lower() == category.lower()]

    def exercises_for(self, category: str, level: str | None = None, n: int = 4) -> list[dict]:
        items = [e for e in self.exercises if e["category"] == category]
        if level:
            preferred = [e for e in items if e["level"] == level]
            items = preferred + [e for e in items if e not in preferred]
        return items[:n]

    LEVELS = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}

    def exercises_by_muscles(
        self, muscles: set[str], level: str = "Beginner", n: int = 3, exclude: set[str] | None = None
    ) -> list[dict]:
        """Strength exercises that train any of the given muscles, closest to the user's level first."""
        exclude = exclude or set()
        target = self.LEVELS.get(level, 0)
        pool = [
            e for e in self.exercises
            if e["category"] == "Strength"
            and e["title"] not in exclude
            and muscles & set(e["muscles"])
        ]
        pool.sort(key=lambda e: abs(self.LEVELS.get(e["level"], 0) - target))
        return pool[:n]
