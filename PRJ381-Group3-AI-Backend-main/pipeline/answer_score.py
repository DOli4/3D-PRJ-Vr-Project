# pipeline/answer_score.py
"""
Scores a student's answer using weighted combinations of scoring modules.
Supports custom per-question weights or defaults based on question type.
"""

import os, sys, json
from typing import Dict
import nltk

# Ensure NLTK punkt tokenizer is available
nltk.download("punkt", quiet=True)

# Fix path import to reach utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.score import (
    score_similarity,
    score_keyword,
    score_sentiment,
    score_star,
    score_completeness,
    score_clarity,
    score_structure,
    score_depth,
    score_outcome,
)

FEEDBACK_MESSAGES = {
    "similarity": {
        "100": "Excellent alignment with the ideal responses. Keep up the clear and focused answers.",
        "75": "Good alignment. Try adding more depth or examples to make your answer even stronger.",
        "50": "Some alignment detected. Review the key ideas from the ideal responses to close the gap.",
        "25": "Your answers only slightly match the ideal responses. Try including more specific details.",
        "0": "No meaningful alignment found. Review the topic and aim to reflect key concepts clearly."
    },
    "keywords": {
        "100": "You’ve used all the key terms expected in your answers. Great job!",
        "75": "Most key terms are present. You could boost impact by weaving them in more naturally.",
        "50": "Some keywords are used. Consider including more specific terms related to the topic.",
        "25": "Few keywords were found. Try to focus on important technical or contextual words.",
        "0": "None of the expected keywords were detected. Review the terminology used in ideal responses."
    },
    "completeness": {
        "100": "Your answers are fully developed and address all key points.",
        "75": "Mostly complete answers. Consider elaborating slightly more on some areas.",
        "50": "Answers are partially complete. Add more details to cover all aspects.",
        "25": "Your responses are brief and miss several key ideas. Try to expand your answers.",
        "0": "Responses are incomplete or very limited. Aim for thoroughness in addressing the question."
    },
    "clarity": {
        "100": "Your answers are exceptionally clear and well-articulated.",
        "75": "Mostly clear. Some ideas could be expressed more directly or simply.",
        "50": "Some parts are clear, but others are hard to follow. Try to simplify your language.",
        "25": "Your answers lack clarity. Break down your thoughts into clearer points.",
        "0": "The writing is difficult to understand. Consider rephrasing and improving sentence flow."
    },
    "structure": {
        "100": "Your answers follow a logical and well-structured format (e.g., STAR).",
        "75": "Generally well-structured. Consider making transitions between points smoother.",
        "50": "Some structure is present. Strengthen your organization using a framework like STAR.",
        "25": "Structure is weak. Try to break answers into clear parts like situation, action, and result.",
        "0": "No clear structure detected. Organize your response logically to improve readability."
    },
    "sentiment": {
        "100": "Your tone is confident, positive, and professional.",
        "75": "Generally positive tone. Ensure consistency and confidence in your wording.",
        "50": "Tone varies or seems neutral. Try to project confidence in your answers.",
        "25": "Tone feels flat or uncertain. Use stronger language to show enthusiasm.",
        "0": "Tone is unclear or negative. Focus on sounding professional and self-assured."
    },
    "depth": {
        "100": "Your answers show impressive insight and deep understanding.",
        "75": "Good depth of thought. Consider including additional context or reasoning.",
        "50": "Some thoughtful points. You can go further in exploring your reasoning.",
        "25": "Answers feel surface-level. Add explanation or analysis to deepen your response.",
        "0": "Very limited depth. Try to elaborate with examples, reasoning, or technical details."
    },
    "outcome": {
        "100": "You clearly communicate results and outcomes. Well done!",
        "75": "Outcomes are mentioned but could be clearer or more quantified.",
        "50": "Some indication of results. Consider highlighting specific impact or improvements.",
        "25": "Limited mention of outcomes. Add concrete results to show value.",
        "0": "No outcomes stated. Try to include what was achieved or learned."
    }
}


def _default_weights(q_type: str) -> Dict[str, float]:
    q_type = q_type.lower()
    return {
        "objective": {
            "similarity": 0.40,
            "keywords": 0.25,
            "completeness": 0.15,
            "clarity": 0.10,
            "structure": 0.05,
            "sentiment": 0.0,
            "depth": 0.05,
            "outcome": 0.0,
        },
        "situational": {
            "similarity": 0.25,
            "keywords": 0.15,
            "completeness": 0.15,
            "clarity": 0.10,
            "structure": 0.10,
            "sentiment": 0.10,
            "depth": 0.10,
            "outcome": 0.05,
        },
        "behavioral": {
            "similarity": 0.20,
            "keywords": 0.15,
            "completeness": 0.15,
            "clarity": 0.10,
            "structure": 0.20,
            "sentiment": 0.10,
            "depth": 0.05,
            "outcome": 0.05,
        },
        "soft_skill": {
            "similarity": 0.10,
            "keywords": 0.10,
            "completeness": 0.15,
            "clarity": 0.20,
            "structure": 0.15,
            "sentiment": 0.20,
            "depth": 0.05,
            "outcome": 0.05,
        },
        "opinion": {
            "similarity": 0.05,
            "keywords": 0.05,
            "completeness": 0.10,
            "clarity": 0.15,
            "structure": 0.25,
            "sentiment": 0.25,
            "depth": 0.05,
            "outcome": 0.10,
        },
    }.get(q_type, {})

def score_answer(data: Dict) -> Dict:
    q_type = (data.get("type") or "").lower()
    weights = data.get("weights") or _default_weights(q_type)

    if not weights:
        return {
            "modules": {},
            "final_score": 0.0,
            "flags": [f"Unsupported or unweighted question type: '{q_type}'"],
        }

    result = {
        "modules": {},
        "final_score": 0.0,
    }

    module_funcs = {
        "similarity": score_similarity,
        "keywords": score_keyword,
        "completeness": score_completeness,
        "clarity": score_clarity,
        "structure": score_structure,
        "sentiment": score_sentiment,
        "depth": score_depth,
        "outcome": score_outcome,
    }

    final_score = 0.0

    for mod_name, weight in weights.items():
        if weight <= 0:
            continue
        func = module_funcs.get(mod_name)
        try:
            module_result = func(data)
            if not isinstance(module_result, dict):
                raise ValueError(f"{mod_name} did not return a dictionary")
        except Exception as e:
            module_result = {"score": 0.0, "error": str(e)}
        result["modules"][mod_name] = module_result
        final_score += weight * module_result.get("score", 0.0)

    result["final_score"] = round(final_score, 3)
    return result

def get_feedback(grades: list) -> list:
    """
    Returns a list of feedback dicts per module:
    { module, avg_score, message }
    """
    module_totals = {}
    module_counts = {}

    for grade in grades:
        if not isinstance(grade, dict):
            continue
        for module, details in grade.items():
            if not isinstance(details, dict):
                continue
            score = details.get("score")
            if score is None:
                continue
            module_totals[module] = module_totals.get(module, 0.0) + score
            module_counts[module] = module_counts.get(module, 0) + 1

    module_averages = {
        module: round(module_totals[module] / module_counts[module], 3)
        for module in module_totals
    }

    feedback = []
    for module, avg_score in module_averages.items():
        if module not in FEEDBACK_MESSAGES:
            continue

        if avg_score >= 0.875:
            tier = "100"
        elif avg_score >= 0.625:
            tier = "75"
        elif avg_score >= 0.375:
            tier = "50"
        elif avg_score >= 0.125:
            tier = "25"
        else:
            tier = "0"

        feedback.append({
            "module": module,
            "avg_score": avg_score,
            "message": FEEDBACK_MESSAGES[module][tier]
        })

    return feedback


def average_modules(session_id: str = None) -> Dict[str, float]:
    """
    Returns a dictionary with average scores for each scoring module.
    This can be used to provide overall performance metrics.
    """

    session
    # Placeholder implementation, replace with actual logic to calculate averages
    return {
        "similarity": 0.8,
        "keywords": 0.75,
        "completeness": 0.7,
        "clarity": 0.85,
        "structure": 0.9,
        "sentiment": 0.8,
        "depth": 0.75,
        "outcome": 0.7,
    }

# Example usage:
if __name__ == "__main__":
    example_data = {
        "id": "sysadmin-hard-001",
        "question": "How do you handle tight deadlines?",
        "role": "sysadmin",
        "difficulty": "hard",
        "type": "situational",
        "student": "I try to avoid working under pressure and usually ask for extensions.",
        "ideal": [
            "I manage tight deadlines by breaking down tasks, prioritising high-impact activities and staying focused under pressure.",
            "I create a schedule and collaborate with colleagues to ensure that we meet critical milestones without sacrificing quality.",
            "I stay calm and organised, often using task trackers to monitor progress and communicate proactively with stakeholders."
        ],
        "keywords": ["deadlines", "time management", "prioritise", "schedule", "pressure"],
        "weights": {"similarity": 0.25, "keywords": 0.2, "completeness": 0.2, "clarity": 0.1, "structure": 0.15, "sentiment": 0.05, "depth": 0.05, "outcome": 0.0}
    }
    score = score_answer(example_data)
    json.dump(score, sys.stdout, indent=2)
    print("\nScore calculated successfully.")