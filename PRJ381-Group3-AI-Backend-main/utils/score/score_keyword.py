# utils/score/score_keyword.py
"""
Calculates keyword coverage by comparing student's answer to expected keywords.

Uses tokenisation, stop-word removal, and stemming to detect coverage.
Returns a match score and list of matched keywords.
"""

from typing import Dict, List
from ._text_processing import tokenize, stem_tokens, filter_stopwords

def get_keyword_score(data: Dict) -> Dict:
    """
    Computes how many expected keywords are present in the student's answer.

    Returns a score (0-1) and the list of matched keywords.
    """
    if ("answer" not in data and "student" not in data) or "keywords" not in data:
        raise ValueError("data must contain 'answer' (or 'student') and 'keywords' keys")

    student_answer: str = data.get("answer", data.get("student", ""))
    keywords: List[str] = data["keywords"]

    tokens = tokenize(student_answer)
    tokens = filter_stopwords(tokens)
    stems = set(stem_tokens(tokens))

    stemmed_keywords = [(kw, stem_tokens([kw.lower()])[0]) for kw in keywords]
    matches = [kw for kw, stem_kw in stemmed_keywords if stem_kw in stems]
    score = round(len(matches) / len(keywords), 3) if keywords else 0.0

    return {
        "score": score,
        "matches": matches,
    }
