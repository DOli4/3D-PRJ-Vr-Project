# utils/score/score_outcome.py
"""
Detects whether a student mentioned the outcome/result of their actions.
Applies to narrative question types and returns a binary score (0 or 1).
"""

from typing import Dict
from .score_star import detect_star_structure

def get_outcome_score(data: Dict) -> Dict:
    answer = data.get("answer", data.get("student", ""))
    q_type = (data.get("type") or "").lower()

    if q_type not in {"situational", "behavioral", "soft_skill", "opinion"}:
        return {"score": 0.0}
    if not answer:
        return {"score": 0.0}

    star_res = detect_star_structure(data)
    if star_res["star_flags"].get("result", False):
        return {"score": 1.0}

    outcome_phrases = [
        "outcome", "result", "impact", "achieved", "improvement", "led to",
        "as a result", "therefore", "finally", "consequently",
    ]
    if any(p in answer.lower() for p in outcome_phrases):
        return {"score": 1.0}

    return {"score": 0.0}
