# utils/score/score_similarity.py
"""
Computes semantic similarity between a student's answer and a list of ideal answers.

Uses sentence embeddings when available, or falls back to TF-IDF with cosine similarity.
Returns the best score, all variant scores, and the method used.
"""

from typing import Dict, List

try:
    from sentence_transformers import SentenceTransformer, util  # type: ignore
    _SENTENCE_TRANSFORMER_AVAILABLE = True
except ImportError:
    _SENTENCE_TRANSFORMER_AVAILABLE = False
    SentenceTransformer = None  # type: ignore[assignment]
    util = None  # type: ignore[assignment]

if _SENTENCE_TRANSFORMER_AVAILABLE:
    _model: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")  # type: ignore[name-defined]
else:
    _model = None  # type: ignore[assignment]


def get_similarity_score(data: Dict) -> Dict:
    """
    Calculates semantic similarity between a student's answer and ideal answers.

    Returns the highest score, per-answer scores, and the method used ("sentence-transformer" or "tfidf").
    """
    if ("answer" not in data and "student" not in data) or "ideal" not in data:
        raise ValueError("data must contain 'answer' (or 'student') and 'ideal' keys")

    student_answer: str = data.get("answer", data.get("student", ""))
    ideal_answers: List[str] = data["ideal"]

    if _SENTENCE_TRANSFORMER_AVAILABLE and _model is not None:
        student_emb = _model.encode(student_answer, convert_to_tensor=True)
        ideal_embs = _model.encode(ideal_answers, convert_to_tensor=True)
        sims_tensor = util.cos_sim(student_emb, ideal_embs)[0]  # type: ignore[operator]
        scores = [round(float(s), 3) for s in sims_tensor]
        best_score = max(scores) if scores else 0.0
        return {
            "score": best_score,
            "variant_scores": scores,
            "engine": "sentence-transformer"
        }
    else:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        corpus = [student_answer] + ideal_answers
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(corpus)
        sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        scores = [round(float(v), 3) for v in sims]
        best_score = max(scores) if scores else 0.0
        return {
            "score": best_score,
            "variant_scores": scores,
            "engine": "tfidf"
        }
