"""
Lightweight text processing helpers.

This module provides basic utilities for tokenising English text,
removing stop words and stemming words. It avoids heavy NLP
dependencies such as spaCy. The stop word list here is a small set
of common English function words. Stemming uses NLTK's
``PorterStemmer`` which is available without external downloads.
"""

import re
from typing import List, Iterable

from nltk.stem import PorterStemmer

# A minimal stop word list for English.
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "if", "while", "to", "of", "in",
    "on", "at", "for", "by", "with", "is", "are", "was", "were", "be",
    "been", "being", "as", "that", "this", "these", "those", "there",
    "their", "they", "them", "he", "she", "his", "her", "it", "its", "my",
    "your", "you", "we", "us", "our", "ours", "do", "does", "did", "not",
    "so", "such", "just", "had", "has", "have", "from", "about", "into",
    "up", "down", "over", "under", "again", "further", "then", "once",
    "here", "there", "when", "where", "why", "how", "all", "any", "both",
    "each", "few", "more", "most", "other", "some", "than", "too", "very",
}

_stemmer = PorterStemmer()


def tokenize(text: str) -> List[str]:
    """Tokenise text into lowercase alphabetic tokens."""
    # Extract sequences of alphabetic characters as words
    tokens = re.findall(r"[A-Za-z]+", text)
    return [t.lower() for t in tokens]


def stem_tokens(tokens: Iterable[str]) -> List[str]:
    """Stem an iterable of tokens using the Porter stemmer."""
    return [_stemmer.stem(tok) for tok in tokens]


def filter_stopwords(tokens: Iterable[str]) -> List[str]:
    """Remove stop words from an iterable of tokens."""
    return [tok for tok in tokens if tok not in STOP_WORDS]