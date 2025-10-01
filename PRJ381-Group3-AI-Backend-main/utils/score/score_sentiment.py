# utils/score/score_sentiment.py
"""
Evaluates how well a student's tone matches the expected tone of ideal answers.

Uses a lexicon-based method to infer sentiment polarity. Lightweight and offline-friendly.
"""

from typing import Dict, List

_POSITIVE_WORDS = {
    "good", "great", "excellent", "positive", "satisfied", "happy",
    "efficient", "successful", "beneficial", "improved", "helpful",
    "effective", "love", "like", "enjoy", "awesome", "fantastic",
    "amazing", "outstanding", "wonderful", "best", "friendly",
    "encouraging", "productive", "clear", "approachable",
}

_NEGATIVE_WORDS = {
    "bad", "poor", "negative", "unsatisfied", "angry", "sad",
    "inefficient", "problem", "issue", "risk", "fail", "failure",
    "difficult", "hard", "hate", "dislike", "problematic",
    "frustrating", "worst", "terrible", "error", "confusing",
    "challenging", "slow", "unclear", "limited",
}

def _compute_polarity(text: str) -> float:
    words = [w.strip(".,!?;:()[]{}'\"").lower() for w in text.split()]
    pos = sum(1 for w in words if w in _POSITIVE_WORDS)
    neg = sum(1 for w in words if w in _NEGATIVE_WORDS)
    total = pos + neg
    return (pos - neg) / total if total > 0 else 0.0

def _label_from_polarity(p: float) -> str:
    if p > 0.05:
        return "positive"
    elif p < -0.05:
        return "negative"
    return "neutral"

def _infer_expected_tone(ideal_answers: List[str]) -> str:
    counts = {"positive": 0, "negative": 0, "neutral": 0}
    for ans in ideal_answers:
        lbl = _label_from_polarity(_compute_polarity(ans))
        counts[lbl] += 1
    if counts["positive"] > max(counts["negative"], counts["neutral"]):
        return "positive"
    elif counts["negative"] > max(counts["positive"], counts["neutral"]):
        return "negative"
    return "neutral"

def _score_sentiment_match(expected: str, actual: str, confidence: float) -> float:
    if expected == actual:
        return 1.0 if expected == "neutral" else round(confidence, 4)
    return 1 - round(confidence, 4)


def get_sentiment_score(data: Dict) -> Dict:
    student_answer = data.get("answer", data.get("student", ""))
    ideal_answers = data.get("ideal", [])

    expected = _infer_expected_tone(ideal_answers) if ideal_answers else "neutral"
    polarity = _compute_polarity(student_answer)
    actual_label = _label_from_polarity(polarity)
    confidence = abs(polarity)

    return {
        "score": _score_sentiment_match(expected, actual_label, confidence),
        "target": expected,
        "label": actual_label,
        "confidence": round(confidence, 4),
    }
