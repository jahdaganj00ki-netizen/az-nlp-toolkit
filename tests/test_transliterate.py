"""Tests for Azerbaijani Latin <-> Cyrillic transliteration."""

import pytest
from az_nlp.transliterate import AzTransliterator


@pytest.fixture
def transliterator():
    return AzTransliterator()


class TestLatinToCyrillic:
    """Test Latin -> Cyrillic transliteration."""

    def test_simple_word(self, transliterator):
        result = transliterator.to_cyrillic("Bakı")
        assert result == "Баky" or "Бак" in result  # Allow flexibility
        # More precise check: each char should map
        assert transliterator.to_cyrillic("a") == "а"
        assert transliterator.to_cyrillic("b") == "б"

    def test_schwa_character(self, transliterator):
        """Ə/ə should map to Ә/ә."""
        assert transliterator.to_cyrillic("ə") == "ә"
        assert transliterator.to_cyrillic("Ə") == "Ә"

    def test_special_az_letters(self, transliterator):
        """Test AZ-specific Latin letters."""
        assert transliterator.to_cyrillic("ç") == "ч"
        assert transliterator.to_cyrillic("ş") == "ш"
        assert transliterator.to_cyrillic("ğ") == "ғ"
        assert transliterator.to_cyrillic("ö") == "ө"
        assert transliterator.to_cyrillic("ü") == "ү"
        assert transliterator.to_cyrillic("ı") == "ы"

    def test_preserves_spaces_and_punctuation(self, transliterator):
        result = transliterator.to_cyrillic("Salam, dünya!")
        assert "," in result
        assert "!" in result
        assert " " in result

    def test_empty_string(self, transliterator):
        assert transliterator.to_cyrillic("") == ""

    def test_numbers_preserved(self, transliterator):
        result = transliterator.to_cyrillic("2024")
        assert result == "2024"


class TestCyrillicToLatin:
    """Test Cyrillic -> Latin transliteration."""

    def test_basic_mapping(self, transliterator):
        assert transliterator.to_latin("а") == "a"
        assert transliterator.to_latin("б") == "b"
        assert transliterator.to_latin("в") == "v"

    def test_special_az_cyrillic(self, transliterator):
        """Test AZ-specific Cyrillic letters."""
        assert transliterator.to_latin("ә") == "ə"
        assert transliterator.to_latin("ч") == "ç"
        assert transliterator.to_latin("ш") == "ş"
        assert transliterator.to_latin("ғ") == "ğ"
        assert transliterator.to_latin("ө") == "ö"
        assert transliterator.to_latin("ү") == "ü"
        assert transliterator.to_latin("ы") == "ı"

    def test_cyrillic_je(self, transliterator):
        """Ҹ/ҹ is unique to AZ Cyrillic -> maps to C/c."""
        assert transliterator.to_latin("ҹ") == "c"
        assert transliterator.to_latin("Ҹ") == "C"

    def test_preserves_non_cyrillic(self, transliterator):
        result = transliterator.to_latin("123 - тест")
        assert "123" in result
        assert "-" in result


class TestScriptDetection:
    """Test automatic script detection."""

    def test_detect_latin(self, transliterator):
        assert transliterator.detect_script("Salam dünya") == "latin"

    def test_detect_cyrillic(self, transliterator):
        assert transliterator.detect_script("Салам дүнйа") == "cyrillic"

    def test_detect_unknown(self, transliterator):
        assert transliterator.detect_script("123 456") == "unknown"


class TestAutoTransliterate:
    """Test automatic transliteration."""

    def test_auto_to_latin(self, transliterator):
        cyrillic = "Салам"
        result = transliterator.auto_transliterate(cyrillic, target="latin")
        # Should convert from Cyrillic to Latin
        assert result != cyrillic  # Should have changed

    def test_auto_to_cyrillic(self, transliterator):
        latin = "Salam"
        result = transliterator.auto_transliterate(latin, target="cyrillic")
        assert result != latin  # Should have changed

    def test_auto_same_script(self, transliterator):
        """If text is already in target script, return unchanged."""
        latin = "Salam"
        result = transliterator.auto_transliterate(latin, target="latin")
        assert result == latin


class TestRoundTrip:
    """Test that Latin -> Cyrillic -> Latin preserves text for basic cases."""

    def test_simple_roundtrip(self, transliterator):
        original = "salam"
        cyrillic = transliterator.to_cyrillic(original)
        back = transliterator.to_latin(cyrillic)
        assert back == original

    def test_vowels_roundtrip(self, transliterator):
        """Test that AZ-specific vowels survive a round trip."""
        for char in ["ə", "ö", "ü", "ı"]:
            cyrillic = transliterator.to_cyrillic(char)
            back = transliterator.to_latin(cyrillic)
            assert back == char, f"Round-trip failed for '{char}'"
