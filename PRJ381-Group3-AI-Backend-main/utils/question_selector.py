# utils/question_selector.py
"""
Selects interview questions by role and difficulty level.

Uses a configurable strategy to sample questions based on an overall level from 1 to 7.
Higher levels yield more difficult questions.
"""

import json
import os
import random
import logging
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent / "interview" / "roles"

# Maps level (1–7) to (easy, medium, hard) counts for 10-question sets
_LEVEL_DISTRIBUTION = {
    1: (6, 3, 1),
    2: (5, 3, 2),
    3: (4, 3, 3),
    4: (3, 3, 4),
    5: (3, 2, 5),
    6: (2, 2, 6),
    7: (1, 2, 7),
}

def _load_questions(role: str, difficulty: str) -> List[Dict]:
    """Load questions for a given role and difficulty."""
    filename = f"{role}_{difficulty}.json"
    path = os.path.join(BASE_DIR, role, filename)

    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            questions = []
            for d in data:
                if not isinstance(d, dict):
                    raise ValueError(f"Invalid question format in {filename}")
                if "id" not in d or "question" not in d:
                    raise ValueError(f"Missing 'id' or 'question' in {filename}")

                questions.append({
                    "id": d.get("id"),
                    "question": d.get("question"),
                    "role": role,
                    "difficulty": difficulty,
                    "type": d.get("type", None),
                    "ideal": d.get("ideal", []),
                    "keywords": d.get("keywords", []),
                    "weights": d.get("weights", {})
                })
            return questions
    except Exception as e:
        return []


def select_questions_by_level(role: str, level: int) -> List[Dict]:
    level = max(1, min(level, 7))
    num_easy, num_medium, num_hard = _LEVEL_DISTRIBUTION[level]

    easy_qs_full = _load_questions(role, "easy")
    med_qs_full = _load_questions(role, "medium")
    hard_qs_full = _load_questions(role, "hard")

    selected: List[Dict] = []

    if easy_qs_full:
        sampled_easy = random.sample(easy_qs_full, min(num_easy, len(easy_qs_full)))
        selected += [{"id": q["id"], "question": q["question"]} for q in sampled_easy]

    if med_qs_full:
        sampled_med = random.sample(med_qs_full, min(num_medium, len(med_qs_full)))
        selected += [{"id": q["id"], "question": q["question"]} for q in sampled_med]

    if hard_qs_full:
        sampled_hard = random.sample(hard_qs_full, min(num_hard, len(hard_qs_full)))
        selected += [{"id": q["id"], "question": q["question"]} for q in sampled_hard]

    random.shuffle(selected)
    return selected


def find_question_by_id(role: str, question_id: str) -> Optional[Dict]:
    """
    Search for a specific question by ID within all difficulty files for a given role.
    """
    for difficulty in ["easy", "medium", "hard"]:
        questions = _load_questions(role, difficulty)
        for q in questions:
            if q.get("id") == question_id:
                return q
    return None

if __name__ == "__main__":
    import os, sys, json, time
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

    role = "sysadmin"
    level = 6

    print(f"🔍 Selecting questions for role='{role}', level={level}\n")

    selected = select_questions_by_level(role, level)

    if not selected:
        print("⚠️ No questions were selected.")
    else:
        print(f"✅ Selected {len(selected)} question(s):")
        time.sleep(5)
        print(json.dumps(selected, indent=2))
