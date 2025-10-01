# utils/score/score_completeness.py
"""
Scores how completely a student's answer covers the content of the ideal answers.
Uses stemmed token overlap to compute an F1 score, along with precision and recall.
"""

from typing import Dict, List, Set
from ._text_processing import tokenize, filter_stopwords, stem_tokens

def _extract_content_tokens(text: str) -> Set[str]:
    tokens = tokenize(text)
    tokens = filter_stopwords(tokens)
    return set(stem_tokens(tokens))

def get_completeness_score(data: Dict) -> Dict:
    """
    Computes an F1-style completeness score between student and ideal answers.
    """
    student_answer = data.get("answer", data.get("student", ""))
    ideal_answers = data.get("ideal", [])

    if not student_answer or not ideal_answers:
        return {"score": 0.0, "precision": 0.0, "recall": 0.0}

    student_tokens = _extract_content_tokens(student_answer)
    ideal_tokens: Set[str] = set()
    for ans in ideal_answers:
        ideal_tokens.update(_extract_content_tokens(ans))

    if not student_tokens or not ideal_tokens:
        return {"score": 0.0, "precision": 0.0, "recall": 0.0}

    intersection = student_tokens & ideal_tokens
    precision = len(intersection) / len(student_tokens)
    recall = len(intersection) / len(ideal_tokens)

    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)

    return {
        "score": round(f1, 3),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
    }
