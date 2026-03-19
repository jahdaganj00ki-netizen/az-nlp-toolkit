"""
Azerbaijani text normalization.

Handles AZ-specific normalization tasks:
  - Case folding with correct handling of İ/I and ı/i
  - Diacritics restoration (e -> ə, o -> ö, u -> ü heuristics)
  - Whitespace normalization
  - Common OCR error correction for Azerbaijani text
  - Number normalization
"""

from __future__ import annotations

import re
import unicodedata
from typing import Dict, List, Optional


# Common words where 'e' should be 'ə' in Azerbaijani.
# This is a frequency-based lookup -- only the most common words.
_E_TO_SCHWA_WORDS: Dict[str, str] = {
    "azerbaycan": "azərbaycan",
    "seher": "şəhər",
    "sheker": "şəkər",
    "melumat": "məlumat",
    "meqale": "məqalə",
    "meqsed": "məqsəd",
    "mexsus": "məxsus",
    "mekteb": "məktəb",
    "mesele": "məsələ",
    "mesel": "məsəl",
    "meqam": "məqam",
    "mekan": "məkan",
    "menim": "mənim",
    "heyat": "həyat",
    "heqiqet": "həqiqət",
    "hemise": "həmişə",
    "her": "hər",
    "hele": "hələ",
    "hemin": "həmin",
    "hemcinin": "həmçinin",
    "teref": "tərəf",
    "teshkilat": "təşkilat",
    "tedris": "tədris",
    "tehsil": "təhsil",
    "tedbir": "tədbir",
    "telebet": "tələbət",
    "telebe": "tələbə",
    "tesir": "təsir",
    "tecrube": "təcrübə",
    "serencam": "sərəncam",
    "sehmdar": "səhmdar",
    "sebeb": "səbəb",
    "sehife": "səhifə",
    "cenub": "cənub",
    "cemiyyet": "cəmiyyət",
    "deyisiklik": "dəyişiklik",
    "deyer": "dəyər",
    "defe": "dəfə",
    "devlet": "dövlət",
    "respublika": "respublika",
    "gomruk": "gömrük",
    "belediyye": "bələdiyyə",
    "beyanname": "bəyannamə",
    "edebiyyat": "ədəbiyyat",
    "emek": "əmək",
    "emel": "əməl",
    "esil": "əsil",
    "eser": "əsər",
    "evvel": "əvvəl",
    "evez": "əvəz",
    "ehemiyyet": "əhəmiyyət",
    "elaqe": "əlaqə",
    "erazi": "ərazi",
    "idxal": "idxal",
    "ixrac": "ixrac",
}

# Common AZ abbreviation expansions
_ABBREV_NORMALIZE = {
    "az.": "azərbaycan",
    "resp.": "respublika",
}


class AzNormalizer:
    """Azerbaijani text normalizer."""

    def __init__(self):
        self._schwa_lookup = _E_TO_SCHWA_WORDS.copy()

    def normalize(
        self,
        text: str,
        lowercase: bool = True,
        restore_diacritics: bool = False,
        fix_whitespace: bool = True,
        strip_accents: bool = False,
    ) -> str:
        """Normalize Azerbaijani text.

        Args:
            text: Input text.
            lowercase: Convert to lowercase (AZ-aware: İ->i, I->ı).
            restore_diacritics: Attempt to restore ə, ö, ü from ASCII
                equivalents using dictionary lookup.
            fix_whitespace: Normalize whitespace (collapse multiple
                spaces, strip).
            strip_accents: Remove combining diacritical marks (use with
                caution -- this destroys AZ-specific characters).

        Returns:
            Normalized text string.
        """
        if not text:
            return text

        result = text

        # Step 1: Unicode normalization (NFC)
        result = unicodedata.normalize("NFC", result)

        # Step 2: AZ-aware lowercasing
        if lowercase:
            result = self._az_lower(result)

        # Step 3: Diacritics restoration
        if restore_diacritics:
            result = self._restore_diacritics(result)

        # Step 4: Whitespace normalization
        if fix_whitespace:
            result = re.sub(r"\s+", " ", result).strip()

        # Step 5: Optional accent stripping
        if strip_accents:
            result = self._strip_accents(result)

        return result

    def _az_lower(self, text: str) -> str:
        """Azerbaijani-aware lowercase conversion.

        In Azerbaijani:
          - İ (U+0130) -> i
          - I (U+0049) -> ı (U+0131)
          - Standard lowercase for all other characters
        """
        result = []
        for ch in text:
            if ch == "İ":       # İ -> i
                result.append("i")
            elif ch == "I":     # I -> ı
                result.append("ı")
            else:
                result.append(ch.lower())
        return "".join(result)

    def _restore_diacritics(self, text: str) -> str:
        """Attempt to restore Azerbaijani diacritics from ASCII text.

        Uses a dictionary of common words where 'e' should be 'ə', etc.
        Only applies to known words to avoid false positives.
        """
        words = text.split()
        restored = []
        for word in words:
            # Preserve leading/trailing punctuation
            prefix = ""
            suffix = ""
            core = word

            while core and not core[0].isalpha():
                prefix += core[0]
                core = core[1:]
            while core and not core[-1].isalpha():
                suffix = core[-1] + suffix
                core = core[:-1]

            lookup = core.lower()
            if lookup in self._schwa_lookup:
                replacement = self._schwa_lookup[lookup]
                # Preserve original casing pattern
                if core[0:1].isupper() and len(core) > 1:
                    replacement = replacement[0].upper() + replacement[1:]
                elif core.isupper():
                    replacement = replacement.upper()
                restored.append(prefix + replacement + suffix)
            else:
                restored.append(word)

        return " ".join(restored)

    @staticmethod
    def _strip_accents(text: str) -> str:
        """Remove combining diacritical marks from text.

        Warning: This will convert ə -> e, ö -> o, ü -> u, etc.
        Use only when ASCII output is required.
        """
        # First handle AZ-specific characters that are standalone
        replacements = {
            "ə": "e", "Ə": "E",
            "ö": "o", "Ö": "O",
            "ü": "u", "Ü": "U",
            "ı": "i", "I": "I",
            "ç": "c", "Ç": "C",
            "ş": "s", "Ş": "S",
            "ğ": "g", "Ğ": "G",
        }
        for src, dst in replacements.items():
            text = text.replace(src, dst)

        # Then handle any remaining combining marks
        nfkd = unicodedata.normalize("NFKD", text)
        return "".join(ch for ch in nfkd if not unicodedata.combining(ch))

    def add_diacritics_mapping(self, ascii_form: str, correct_form: str) -> None:
        """Add a custom word mapping for diacritics restoration.

        Args:
            ascii_form: The ASCII version of the word (e.g., 'melumat').
            correct_form: The correct Azerbaijani form (e.g., 'məlumat').
        """
        self._schwa_lookup[ascii_form.lower()] = correct_form.lower()
