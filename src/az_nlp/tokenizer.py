"""
Azerbaijani text tokenizer.

Handles AZ-specific abbreviations, decimal numbers with commas/dots,
clitics (da/də attached with hyphen), and sentence boundary detection
aware of common Azerbaijani abbreviations.
"""

from __future__ import annotations

import re
from typing import List


# Common Azerbaijani abbreviations that end with a period but do not
# signal a sentence boundary.
_AZ_ABBREVIATIONS = {
    # Titles
    "cənab", "xanım", "prof", "dos", "akad", "dr",
    # Geographic / administrative
    "şəh", "küç", "pr", "kənd", "ray", "mhz",
    # Units and measures
    "mln", "mlrd", "min", "kq", "km", "sm", "ha",
    # Common short forms
    "və s", "b.e", "e.ə", "m.ö", "h.ə",
    # Organizational
    "MMC", "ASC", "QSC",
}

# Regex: abbreviation followed by a period (case-insensitive)
_ABBREV_PATTERN = re.compile(
    r"\b("
    + "|".join(re.escape(a) for a in sorted(_AZ_ABBREVIATIONS, key=len, reverse=True))
    + r")\.",
    re.IGNORECASE,
)

# Sentence-ending punctuation
_SENT_END = re.compile(r'([.!?]+)\s+')

# Token pattern:
#   - Abbreviations with dots (e.g., "b.e.", "və s.")
#   - Numbers with decimal separators (1.5, 3,14)
#   - Words (including AZ-specific letters: ə, ö, ü, ı, ç, ş, ğ)
#   - Punctuation as separate tokens
_TOKEN_PATTERN = re.compile(
    r"""
    (?:[A-ZÇƏĞIİÖŞÜa-zçəğıiöşü]+\.)+            # abbreviations with dots
    | \d+(?:[.,]\d+)*                                # numbers (1.5 or 3,14)
    | [A-ZÇƏĞIİÖŞÜa-zçəğıiöşü]                    # AZ letters
      (?:[A-ZÇƏĞIİÖŞÜa-zçəğıiöşü'-]*              # word body (may include apostrophe/hyphen)
         [A-ZÇƏĞIİÖŞÜa-zçəğıiöşü])?               # must end with a letter
    | [^\s]                                           # any other non-space char (punctuation)
    """,
    re.VERBOSE | re.UNICODE,
)


class AzTokenizer:
    """Azerbaijani-aware word and sentence tokenizer."""

    def __init__(self, keep_abbrev_dots: bool = True):
        """
        Args:
            keep_abbrev_dots: If True, abbreviation dots are kept as part
                of the token (e.g., "mln." stays as one token). If False,
                the dot is stripped.
        """
        self.keep_abbrev_dots = keep_abbrev_dots

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into a list of word/punctuation tokens.

        Args:
            text: Input Azerbaijani text.

        Returns:
            List of token strings.
        """
        if not text or not text.strip():
            return []

        tokens = _TOKEN_PATTERN.findall(text)

        if not self.keep_abbrev_dots:
            cleaned = []
            for tok in tokens:
                if tok.endswith(".") and tok[:-1].lower().rstrip(".") in _AZ_ABBREVIATIONS:
                    cleaned.append(tok[:-1])
                else:
                    cleaned.append(tok)
            tokens = cleaned

        return tokens

    def sent_tokenize(self, text: str) -> List[str]:
        """Split text into sentences, respecting AZ abbreviations.

        Args:
            text: Input Azerbaijani text.

        Returns:
            List of sentence strings.
        """
        if not text or not text.strip():
            return []

        # Protect abbreviations by replacing their dots with a placeholder
        protected = text
        placeholder = "\x00"  # null byte unlikely in normal text

        abbrev_positions = []
        for match in _ABBREV_PATTERN.finditer(text):
            abbrev_positions.append((match.start(), match.end()))

        # Replace abbreviation dots with placeholder (process in reverse to preserve positions)
        for start, end in reversed(abbrev_positions):
            protected = protected[:end - 1] + placeholder + protected[end:]

        # Split on sentence-ending punctuation
        sentences = []
        last = 0
        for match in _SENT_END.finditer(protected):
            end = match.end()
            sent = protected[last:end].strip()
            if sent:
                sentences.append(sent.replace(placeholder, "."))
            last = end

        # Remainder
        remainder = protected[last:].strip()
        if remainder:
            sentences.append(remainder.replace(placeholder, "."))

        return sentences

    def word_tokenize(self, text: str) -> List[str]:
        """Alias for tokenize(). Returns word tokens only (no punctuation).

        Args:
            text: Input Azerbaijani text.

        Returns:
            List of word token strings (punctuation excluded).
        """
        tokens = self.tokenize(text)
        return [t for t in tokens if re.match(r"[A-ZÇƏĞIİÖŞÜa-zçəğıiöşü]", t)]
