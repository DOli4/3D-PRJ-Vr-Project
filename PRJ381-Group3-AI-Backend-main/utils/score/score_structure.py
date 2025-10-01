# utils/score/score_structure.py
"""
Evaluates how well a student's answer is structured.

Uses STAR score for narrative types and sentence count for others.
"""

from typing import Dict
import re
# import os, sys, json
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", )))
from .score_star import detect_star_structure


def get_structure_score(data: Dict) -> Dict:
    """
    Computes a structure score based on question type.
    """
    answer = data.get("answer", data.get("student", ""))
    q_type = (data.get("type") or "").lower()

    if not answer:
        return {"score": 0.0}

    if q_type in {"situational", "behavioral", "soft_skill", "opinion"}:
        star_result = detect_star_structure(data)
        return {
            "score": star_result["score"],
            "star_flags": star_result["star_flags"],
        }

    sentences = re.split(r"[.!?]+", answer)
    sentences = [s.strip() for s in sentences if s.strip()]
    num_sentences = len(sentences)

    if num_sentences >= 3:
        struct_score = 1.0
    elif num_sentences == 2:
        struct_score = 0.5
    else:
        struct_score = 0.0

    return {
        "score": round(struct_score, 3),
        "num_sentences": num_sentences,
    }

# # Example usage:
# if __name__ == "__main__":
#     example_data = {
#         "id": "sysadmin-hard-001",
#         "question": "How do you handle tight deadlines?",
#         "role": "sysadmin",
#         "difficulty": "hard",
#         "type": "situational",
#         "student": "I try to avoid working under pressure and usually ask for extensions.",
#         "ideal": [
#         "I manage tight deadlines by breaking down tasks, prioritising high-impact activities and staying focused under pressure.",
#         "I create a schedule and collaborate with colleagues to ensure that we meet critical milestones without sacrificing quality.",
#         "I stay calm and organised, often using task trackers to monitor progress and communicate proactively with stakeholders."
#         ],
#         "keywords": ["deadlines", "time management", "prioritise", "schedule", "pressure"],
#         "weights": {"similarity": 0.25, "keywords": 0.2, "completeness": 0.2, "clarity": 0.1, "structure": 0.15, "sentiment": 0.05, "depth": 0.05, "outcome": 0.0}
#     }
#     score = get_structure_score(example_data)
#     json.dump(score, sys.stdout, indent=2)
#     print("\nScore calculated successfully.")