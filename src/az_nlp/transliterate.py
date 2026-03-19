"""
Azerbaijani Latin <-> Cyrillic transliteration.

Implements bidirectional transliteration following the official
Azerbaijani alphabet mappings:
  - Latin (32 letters, adopted 1991): A, B, C, Ç, D, E, Ə, F, G, Ğ, H, X,
    I, İ, J, K, Q, L, M, N, O, Ö, P, R, S, Ş, T, U, Ü, V, Y, Z
  - Cyrillic (32 letters, Soviet era): А, Б, В, Г, Ғ, Д, Е, Ә, Ж, З, И,
    Й, К, Л, М, Н, О, Ө, П, Р, С, Т, У, Ү, Ф, Х, Һ, Ч, Ҹ, Ш, Ы, Э

Special handling:
  - Cyrillic Ж -> Latin J (not "Zh")
  - Cyrillic Ҹ -> Latin C (unique to AZ Cyrillic)
  - Latin Q -> Cyrillic Ғ
  - Latin X -> Cyrillic Х
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


# Direct mappings (hardcoded for reliability, with JSON as reference)

_LATIN_TO_CYRILLIC = {
    "A": "А", "a": "а",
    "B": "Б", "b": "б",
    "C": "Ҹ", "c": "ҹ",
    "Ç": "Ч", "ç": "ч",
    "D": "Д", "d": "д",
    "E": "Е", "e": "е",
    "Ə": "Ә", "ə": "ә",
    "F": "Ф", "f": "ф",
    "G": "Г", "g": "г",
    "Ğ": "Ғ", "ğ": "ғ",
    "H": "Һ", "h": "һ",
    "X": "Х", "x": "х",
    "I": "Ы", "ı": "ы",
    "İ": "И", "i": "и",
    "J": "Ж", "j": "ж",
    "K": "К", "k": "к",
    "Q": "Г", "q": "г",
    "L": "Л", "l": "л",
    "M": "М", "m": "м",
    "N": "Н", "n": "н",
    "O": "О", "o": "о",
    "Ö": "Ө", "ö": "ө",
    "P": "П", "p": "п",
    "R": "Р", "r": "р",
    "S": "С", "s": "с",
    "Ş": "Ш", "ş": "ш",
    "T": "Т", "t": "т",
    "U": "У", "u": "у",
    "Ü": "Ү", "ü": "ү",
    "V": "В", "v": "в",
    "Y": "Й", "y": "й",
    "Z": "З", "z": "з",
}

_CYRILLIC_TO_LATIN = {
    "А": "A", "а": "a",
    "Б": "B", "б": "b",
    "В": "V", "в": "v",
    "Г": "G", "г": "g",
    "Ғ": "Ğ", "ғ": "ğ",
    "Д": "D", "д": "d",
    "Е": "E", "е": "e",
    "Ә": "Ə", "ә": "ə",
    "Ж": "J", "ж": "j",
    "З": "Z", "з": "z",
    "И": "İ", "и": "i",
    "Й": "Y", "й": "y",
    "К": "K", "к": "k",
    "Л": "L", "л": "l",
    "М": "M", "м": "m",
    "Н": "N", "н": "n",
    "О": "O", "о": "o",
    "Ө": "Ö", "ө": "ö",
    "П": "P", "п": "p",
    "Р": "R", "р": "r",
    "С": "S", "с": "s",
    "Т": "T", "т": "t",
    "У": "U", "у": "u",
    "Ү": "Ü", "ү": "ü",
    "Ф": "F", "ф": "f",
    "Х": "X", "х": "x",
    "Һ": "H", "һ": "h",
    "Ч": "Ç", "ч": "ç",
    "Ҹ": "C", "ҹ": "c",
    "Ш": "Ş", "ш": "ş",
    "Ы": "I", "ы": "ı",
    "Э": "E", "э": "e",
}


class AzTransliterator:
    """Bidirectional Azerbaijani Latin <-> Cyrillic transliterator."""

    def __init__(self, mapping_file: Optional[str] = None):
        """
        Args:
            mapping_file: Optional path to a JSON mapping file. If None,
                uses the built-in hardcoded mappings.
        """
        if mapping_file:
            with open(mapping_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._l2c = data.get("latin_to_cyrillic", _LATIN_TO_CYRILLIC)
            self._c2l = data.get("cyrillic_to_latin", _CYRILLIC_TO_LATIN)
        else:
            self._l2c = _LATIN_TO_CYRILLIC.copy()
            self._c2l = _CYRILLIC_TO_LATIN.copy()

    def to_cyrillic(self, text: str) -> str:
        """Convert Azerbaijani Latin text to Cyrillic script.

        Args:
            text: Input text in Latin script.

        Returns:
            Text transliterated to Cyrillic.
        """
        result = []
        for ch in text:
            result.append(self._l2c.get(ch, ch))
        return "".join(result)

    def to_latin(self, text: str) -> str:
        """Convert Azerbaijani Cyrillic text to Latin script.

        Args:
            text: Input text in Cyrillic script.

        Returns:
            Text transliterated to Latin.
        """
        result = []
        for ch in text:
            result.append(self._c2l.get(ch, ch))
        return "".join(result)

    def detect_script(self, text: str) -> str:
        """Detect whether the text is primarily Latin or Cyrillic.

        Args:
            text: Input text.

        Returns:
            'latin', 'cyrillic', or 'mixed'/'unknown'.
        """
        latin_count = 0
        cyrillic_count = 0

        for ch in text:
            if ch in self._l2c:
                latin_count += 1
            if ch in self._c2l:
                cyrillic_count += 1

        if latin_count == 0 and cyrillic_count == 0:
            return "unknown"
        if cyrillic_count > latin_count:
            return "cyrillic"
        if latin_count > cyrillic_count:
            return "latin"
        return "mixed"

    def auto_transliterate(self, text: str, target: str = "latin") -> str:
        """Automatically detect the script and transliterate to target.

        Args:
            text: Input text in either script.
            target: Target script, either 'latin' or 'cyrillic'.

        Returns:
            Text in the target script.
        """
        detected = self.detect_script(text)
        if target == "latin" and detected == "cyrillic":
            return self.to_latin(text)
        elif target == "cyrillic" and detected == "latin":
            return self.to_cyrillic(text)
        return text
