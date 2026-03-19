"""
Rule-based Azerbaijani stemmer.

Azerbaijani is an agglutinative language with vowel harmony. Suffixes
are appended in a specific order: noun stem + plural + possessive + case.
This stemmer strips suffixes iteratively, respecting vowel harmony
classes (back vowels: a, ı, o, u; front vowels: ə, i, ö, ü).

This is a light stemmer -- it handles the most common nominal and verbal
suffixes but does not attempt full morphological analysis.
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple


# Vowel harmony groups
_BACK_VOWELS = set("aıou")
_FRONT_VOWELS = set("əiöü")
_ALL_VOWELS = _BACK_VOWELS | _FRONT_VOWELS

# Minimum stem length after stripping
_MIN_STEM_LENGTH = 2


def _get_vowel_class(word: str) -> Optional[str]:
    """Determine the vowel harmony class of a word based on last vowel.

    Returns:
        'back' if the last vowel is a back vowel,
        'front' if the last vowel is a front vowel,
        None if no vowels found.
    """
    for ch in reversed(word.lower()):
        if ch in _BACK_VOWELS:
            return "back"
        if ch in _FRONT_VOWELS:
            return "front"
    return None


def _has_vowel(word: str) -> bool:
    """Check if the word contains at least one vowel."""
    return any(ch in _ALL_VOWELS for ch in word.lower())


# Suffix rules: (pattern, min_stem_len)
# Order matters -- longer / more specific suffixes first.
# Each suffix is a regex pattern. We try to match and strip from the end.

# Verbal suffixes
_VERBAL_SUFFIXES: List[Tuple[str, int]] = [
    (r"malıdır$", 3),
    (r"məlidir$", 3),
    (r"maqdadır$", 3),
    (r"məkdədir$", 3),
    (r"acaqdır$", 3),
    (r"əcəkdir$", 3),
    (r"ılmışdır$", 3),
    (r"ilmişdir$", 3),
    (r"mışdır$", 3),
    (r"mişdir$", 3),
    (r"acaq$", 3),
    (r"əcək$", 3),
    (r"malı$", 3),
    (r"məli$", 3),
    (r"ıyor$", 3),
    (r"maqda$", 3),
    (r"məkdə$", 3),
    (r"ılmış$", 3),
    (r"ilmiş$", 3),
    (r"mışdı$", 3),
    (r"mişdi$", 3),
    (r"araq$", 3),
    (r"ərək$", 3),
    (r"mış$", 2),
    (r"miş$", 2),
    (r"muş$", 2),
    (r"müş$", 2),
    (r"dır$", 2),
    (r"dir$", 2),
    (r"dur$", 2),
    (r"dür$", 2),
    (r"maq$", 2),
    (r"mək$", 2),
]

# Nominal suffixes -- ordered from longest to shortest
_NOMINAL_SUFFIXES: List[Tuple[str, int]] = [
    # Case + possessive combinations
    (r"larından$", 2),
    (r"lərindən$", 2),
    (r"larında$", 2),
    (r"lərində$", 2),
    (r"larının$", 2),
    (r"lərinin$", 2),
    # Plural + case
    (r"lardan$", 2),
    (r"lərdən$", 2),
    (r"larda$", 2),
    (r"lərdə$", 2),
    (r"lara$", 2),
    (r"lərə$", 2),
    (r"ların$", 2),
    (r"lərin$", 2),
    (r"larla$", 2),
    (r"lərlə$", 2),
    # Possessive + case
    (r"ından$", 2),
    (r"indən$", 2),
    (r"ında$", 2),
    (r"ində$", 2),
    (r"ının$", 2),
    (r"inin$", 2),
    (r"ına$", 2),
    (r"inə$", 2),
    # Plural
    (r"lar$", 2),
    (r"lər$", 2),
    # Case suffixes
    (r"dan$", 2),
    (r"dən$", 2),
    (r"tan$", 2),
    (r"tən$", 2),
    (r"nın$", 2),
    (r"nin$", 2),
    (r"nun$", 2),
    (r"nün$", 2),
    (r"na$", 2),
    (r"nə$", 2),
    (r"da$", 2),
    (r"də$", 2),
    (r"ya$", 2),
    (r"yə$", 2),
    # Possessive
    (r"ımız$", 2),
    (r"imiz$", 2),
    (r"umuz$", 2),
    (r"ümüz$", 2),
    (r"ınız$", 2),
    (r"iniz$", 2),
    (r"unuz$", 2),
    (r"ünüz$", 2),
    (r"ları$", 2),
    (r"ləri$", 2),
    (r"ım$", 2),
    (r"im$", 2),
    (r"um$", 2),
    (r"üm$", 2),
    (r"ın$", 2),
    (r"in$", 2),
    (r"un$", 2),
    (r"ün$", 2),
    # With (instrumental)
    (r"la$", 2),
    (r"lə$", 2),
]

# Derivational suffixes (less aggressive -- only strip if stem is long enough)
_DERIVATIONAL_SUFFIXES: List[Tuple[str, int]] = [
    (r"lıq$", 3),
    (r"lik$", 3),
    (r"luq$", 3),
    (r"lük$", 3),
    (r"çı$", 3),
    (r"çi$", 3),
    (r"çu$", 3),
    (r"çü$", 3),
    (r"sız$", 3),
    (r"siz$", 3),
    (r"suz$", 3),
    (r"süz$", 3),
    (r"lı$", 3),
    (r"li$", 3),
    (r"lu$", 3),
    (r"lü$", 3),
]


class AzStemmer:
    """Rule-based Azerbaijani stemmer using iterative suffix stripping."""

    def __init__(self, aggressive: bool = False):
        """
        Args:
            aggressive: If True, also strips derivational suffixes
                (-lıq, -çı, -sız, -lı, etc.). Default is False
                (only inflectional suffixes).
        """
        self.aggressive = aggressive

    def stem(self, word: str) -> str:
        """Stem a single Azerbaijani word.

        Args:
            word: Input word (should be a single token, lowercase recommended).

        Returns:
            The stemmed form of the word.
        """
        if not word:
            return word

        original = word
        w = word.lower().strip()

        if len(w) <= _MIN_STEM_LENGTH:
            return w

        # Phase 1: Strip verbal suffixes (try once)
        w = self._strip_suffixes(w, _VERBAL_SUFFIXES)

        # Phase 2: Strip nominal suffixes iteratively
        prev = None
        while prev != w and len(w) > _MIN_STEM_LENGTH:
            prev = w
            w = self._strip_suffixes(w, _NOMINAL_SUFFIXES)

        # Phase 3: Derivational (optional)
        if self.aggressive:
            w = self._strip_suffixes(w, _DERIVATIONAL_SUFFIXES)

        # Ensure we have a valid stem
        if len(w) < _MIN_STEM_LENGTH or not _has_vowel(w):
            return original.lower()

        return w

    def stem_tokens(self, tokens: List[str]) -> List[str]:
        """Stem a list of tokens.

        Args:
            tokens: List of word strings.

        Returns:
            List of stemmed strings.
        """
        return [self.stem(t) for t in tokens]

    @staticmethod
    def _strip_suffixes(
        word: str, suffixes: List[Tuple[str, int]]
    ) -> str:
        """Try to strip the first matching suffix from the word.

        Args:
            word: The current word form.
            suffixes: List of (regex_pattern, min_stem_length) tuples.

        Returns:
            The word with the suffix removed, or unchanged if no match.
        """
        for pattern, min_len in suffixes:
            m = re.search(pattern, word)
            if m:
                candidate = word[: m.start()]
                if len(candidate) >= min_len and _has_vowel(candidate):
                    return candidate
        return word
