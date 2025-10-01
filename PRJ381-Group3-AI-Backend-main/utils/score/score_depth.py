# utils/score/score_depth.py
"""
Estimates how much detail a student's answer provides compared to ideal responses.

Scores based on the number of content tokens (length > 3, not stop words).
"""

from typing import Dict, List
from ._text_processing import tokenize, filter_stopwords


def _count_content_tokens(text: str) -> int:
    tokens = tokenize(text)
    tokens = filter_stopwords(tokens)
    return sum(1 for tok in tokens if len(tok) > 3)


def get_depth_score(data: Dict) -> Dict:
    student_answer = data.get("answer", data.get("student", ""))
    ideal_answers: List[str] = data.get("ideal", [])

    if not student_answer or not ideal_answers:
        return {"score": 0.0, "student_count": 0, "ideal_average": 0.0}

    student_count = _count_content_tokens(student_answer)
    ideal_counts = [_count_content_tokens(ans) for ans in ideal_answers]
    ideal_average = sum(ideal_counts) / len(ideal_counts) if ideal_counts else 0.0

    if ideal_average == 0:
        score = 1.0 if student_count > 0 else 0.0
    else:
        score = min(student_count / ideal_average, 1.0)

    return {
        "score": round(score, 3),
        "student_count": student_count,
        "ideal_average": round(ideal_average, 3),
    }
