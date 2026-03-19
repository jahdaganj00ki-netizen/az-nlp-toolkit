"""
Azerbaijani stopwords management.

Loads a curated list of Azerbaijani stopwords from the data directory
and provides methods for filtering token lists.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Set


_DEFAULT_STOPWORDS_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "stopwords_az.txt"
)


def _load_stopwords(filepath: Path) -> Set[str]:
    """Load stopwords from a text file (one word per line, # comments)."""
    words = set()
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                # Handle multi-word stopwords
                words.add(line.lower())
    return words


class AzStopwords:
    """Azerbaijani stopword list and filtering utilities."""

    def __init__(
        self,
        stopwords_path: Optional[str] = None,
        extra_stopwords: Optional[List[str]] = None,
    ):
        """
        Args:
            stopwords_path: Path to a custom stopwords file. If None,
                uses the built-in Azerbaijani stopwords list.
            extra_stopwords: Additional stopwords to add to the set.
        """
        path = Path(stopwords_path) if stopwords_path else _DEFAULT_STOPWORDS_PATH

        if path.exists():
            self._stopwords = _load_stopwords(path)
        else:
            # Fallback minimal set if file not found
            self._stopwords = {
                "və", "bir", "bu", "da", "də", "ilə", "üçün", "ki",
                "o", "mən", "sən", "biz", "siz", "onlar", "var", "yox",
                "idi", "isə", "olan", "olur", "edir", "hər", "çox",
                "daha", "ən", "belə", "necə", "amma", "lakin", "ancaq",
            }

        if extra_stopwords:
            self._stopwords.update(w.lower() for w in extra_stopwords)

    @property
    def words(self) -> Set[str]:
        """Return the full set of stopwords."""
        return self._stopwords.copy()

    def __len__(self) -> int:
        return len(self._stopwords)

    def __contains__(self, word: str) -> bool:
        return word.lower() in self._stopwords

    def is_stopword(self, word: str) -> bool:
        """Check if a word is a stopword.

        Args:
            word: The word to check.

        Returns:
            True if the word is in the stopword list.
        """
        return word.lower() in self._stopwords

    def remove(self, tokens: List[str]) -> List[str]:
        """Remove stopwords from a list of tokens.

        Args:
            tokens: List of word strings.

        Returns:
            Filtered list with stopwords removed.
        """
        return [t for t in tokens if t.lower() not in self._stopwords]

    def add(self, word: str) -> None:
        """Add a word to the stopword set."""
        self._stopwords.add(word.lower())

    def remove_word(self, word: str) -> None:
        """Remove a word from the stopword set."""
        self._stopwords.discard(word.lower())
