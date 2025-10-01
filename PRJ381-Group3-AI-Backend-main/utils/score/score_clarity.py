# utils/score/score_clarity.py
"""
Scores the readability of a student's answer using the Flesch Reading Ease formula.

Returns a normalized score between 0-1, plus sentence, word, and syllable stats.
"""

from typing import Dict
import re

def _count_syllables_in_word(word: str) -> int:
    word = word.lower()
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for char in word:
        if char in vowels:
            if not prev_vowel:
                count += 1
                prev_vowel = True
        else:
            prev_vowel = False
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)

def _count_syllables(text: str) -> int:
    words = [w for w in text.split() if w.isalpha()]
    return sum(_count_syllables_in_word(w) for w in words)

def get_clarity_score(data: Dict) -> Dict:
    text = data.get("answer", data.get("student", ""))
    if not text:
        return {"score": 0.0, "reading_ease": 0.0, "words": 0, "sentences": 0, "syllables": 0}

    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    num_sentences = max(len(sentences), 1)

    words = [w for w in text.split() if any(c.isalpha() for c in w)]
    num_words = max(len(words), 1)

    num_syllables = _count_syllables(text)

    reading_ease = 206.835 - 1.015 * (num_words / num_sentences) - 84.6 * (num_syllables / num_words)
    norm = max(0.0, min(reading_ease / 100.0, 1.0))

    return {
        "score": round(norm, 3),
        "reading_ease": round(reading_ease, 2),
        "words": num_words,
        "sentences": num_sentences,
        "syllables": num_syllables,
    }
