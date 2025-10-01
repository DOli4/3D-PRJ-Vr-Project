# utils/score/score_star.py
"""
Detects the use of the STAR method (Situation, Task, Action, Result) in an answer.
Uses keyword heuristics and an optional NLTK-based fallback for NLP-assisted detection.
"""

from typing import Dict
import re

# Try to use NLTK for fallback enhancement
try:
    import nltk
    from nltk import pos_tag, word_tokenize, download
    from nltk.tokenize import sent_tokenize

    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        download("punkt", quiet=True)

    try:
        nltk.data.find("taggers/averaged_perceptron_tagger")
    except LookupError:
        download("averaged_perceptron_tagger", quiet=True)

    _NLTK_AVAILABLE = True
except Exception:
    _NLTK_AVAILABLE = False

# Expanded keyword sets
SITUATION_TRIGGERS = {
    "during", "while", "at the time", "in a project", "faced with", "encountered",
    "when", "dealing with", "involved in"
}
TASK_TRIGGERS = {
    "my role", "my responsibility", "i had to", "was assigned", "i needed to",
    "my objective", "was tasked", "i was responsible"
}
ACTION_TRIGGERS = {
    "i did", "i created", "i implemented", "i developed", "we worked on",
    "i led", "i organized", "i contributed", "i solved", "i initiated"
}
RESULT_TRIGGERS = {
    "as a result", "in the end", "we achieved", "the outcome", "led to",
    "this resulted in", "this led to", "successfully", "the impact was"
}


def detect_star_structure(data: Dict) -> Dict:
    """
    Identifies STAR elements in a student's answer using phrase matching and optional POS fallback.
    Returns a score, flags, and engine info.
    """
    answer_text = data.get("answer", data.get("student", ""))
    if not answer_text:
        return {
            "score": 0.0,
            "star_flags": {
                "situation": False,
                "task": False,
                "action": False,
                "result": False,
            },
            "engine": "none"
        }

    star_flags = {
        "situation": False,
        "task": False,
        "action": False,
        "result": False,
    }

    found_by_nlp = False
    sentences = re.split(r"[.!?]+", answer_text)
    for raw in sentences:
        s = raw.lower().strip()
        if not s:
            continue
        if not star_flags["situation"] and any(w in s for w in SITUATION_TRIGGERS):
            star_flags["situation"] = True
        if not star_flags["task"] and any(w in s for w in TASK_TRIGGERS):
            star_flags["task"] = True
        if not star_flags["action"] and any(w in s for w in ACTION_TRIGGERS):
            star_flags["action"] = True
        if not star_flags["result"] and any(w in s for w in RESULT_TRIGGERS):
            star_flags["result"] = True

    # NLP fallback to catch missing components (POS-based)
    if _NLTK_AVAILABLE and not all(star_flags.values()):
        for sent in sent_tokenize(answer_text):
            tokens = word_tokenize(sent)
            tags = pos_tag(tokens)
            tag_set = set(tag for word, tag in tags)

            if not star_flags["task"] and ("MD" in tag_set or "VB" in tag_set):
                star_flags["task"] = True
                found_by_nlp = True
            if not star_flags["action"] and any(t.startswith("V") for t in tag_set):
                star_flags["action"] = True
                found_by_nlp = True
            if not star_flags["result"] and any(w.lower() in sent.lower() for w in ["success", "impact", "outcome"]):
                star_flags["result"] = True
                found_by_nlp = True

    score = round(sum(star_flags.values()) / 4, 3)
    engine = "heuristic+nltk" if found_by_nlp else "heuristic"

    return {
        "score": score,
        "star_flags": star_flags,
        "engine": engine
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
#     score = detect_star_structure(example_data)
#     import json, sys
#     json.dump(score, sys.stdout, indent=2)
#     print("\nScore calculated successfully.")
