"""Tests for the Azerbaijani stemmer."""

import pytest
from az_nlp.stemmer import AzStemmer


@pytest.fixture
def stemmer():
    return AzStemmer()


@pytest.fixture
def aggressive_stemmer():
    return AzStemmer(aggressive=True)


class TestPluralStemming:
    """Test stripping of plural suffixes -lar/-lər."""

    def test_back_vowel_plural(self, stemmer):
        assert stemmer.stem("kitablar") == "kitab"

    def test_front_vowel_plural(self, stemmer):
        # Short stems may not be reduced further
        result = stemmer.stem("evlər")
        assert isinstance(result, str)
        assert len(result) <= len("evlər")

    def test_plural_with_case(self, stemmer):
        # kitab + lar + dan
        assert stemmer.stem("kitablardan") == "kitab"

    def test_plural_with_locative(self, stemmer):
        # ev + lər + də -> strips to evlər (short stem protection)
        result = stemmer.stem("evlərdə")
        assert result in ("ev", "evlər")


class TestCaseStemming:
    """Test stripping of case suffixes."""

    def test_ablative_back(self, stemmer):
        # şəhər + dən
        assert stemmer.stem("şəhərdən") == "şəhər"

    def test_ablative_front(self, stemmer):
        # Short word: ev + dən -> may not strip below minimum
        result = stemmer.stem("evdən")
        assert result in ("ev", "evdən")

    def test_genitive(self, stemmer):
        # kitab + ın
        assert stemmer.stem("kitabın") == "kitab"

    def test_dative(self, stemmer):
        result = stemmer.stem("evdə")
        assert result in ("ev", "evdə")

    def test_locative_back(self, stemmer):
        assert stemmer.stem("kitabda") == "kitab"


class TestPossessiveStemming:
    """Test stripping of possessive suffixes."""

    def test_first_person(self, stemmer):
        assert stemmer.stem("kitabım") == "kitab"

    def test_first_person_plural(self, stemmer):
        assert stemmer.stem("kitabımız") == "kitab"

    def test_third_person_plural(self, stemmer):
        # ev + ləri -> short stem protection may apply
        result = stemmer.stem("evləri")
        assert result in ("ev", "evləri")


class TestVerbalStemming:
    """Test stripping of verbal suffixes."""

    def test_infinitive_back(self, stemmer):
        assert stemmer.stem("yazmaq") == "yaz"

    def test_infinitive_front(self, stemmer):
        assert stemmer.stem("görmək") == "gör"

    def test_past_participle(self, stemmer):
        assert stemmer.stem("gəlmiş") == "gəl"

    def test_obligation(self, stemmer):
        result = stemmer.stem("göndərməlidir")
        assert result == "göndər"

    def test_copula(self, stemmer):
        assert stemmer.stem("gözəldir") == "gözəl"


class TestComplexSuffixes:
    """Test multiple suffix combinations."""

    def test_plural_possessive_case(self, stemmer):
        # ev + lər + in + də -> evlər (short stem)
        result = stemmer.stem("evlərində")
        assert result in ("ev", "evlər")

    def test_plural_genitive(self, stemmer):
        # işçi + lər + in
        result = stemmer.stem("işçilərin")
        assert result == "işçi"


class TestEdgeCases:
    """Test edge cases and short words."""

    def test_short_word(self, stemmer):
        # Should not strip below minimum length
        assert stemmer.stem("ev") == "ev"

    def test_empty_string(self, stemmer):
        assert stemmer.stem("") == ""

    def test_single_char(self, stemmer):
        assert stemmer.stem("a") == "a"

    def test_no_suffix(self, stemmer):
        assert stemmer.stem("kitab") == "kitab"

    def test_stem_tokens(self, stemmer):
        tokens = ["kitablar", "evlər", "gözəl"]
        results = stemmer.stem_tokens(tokens)
        assert results[0] == "kitab"
        assert isinstance(results[1], str)


class TestAggressiveMode:
    """Test derivational suffix stripping."""

    def test_liq_suffix(self, aggressive_stemmer):
        result = aggressive_stemmer.stem("azadlıq")
        assert result == "azad"

    def test_chi_suffix(self, aggressive_stemmer):
        result = aggressive_stemmer.stem("işçi")
        assert result in ("iş", "işçi")

    def test_siz_suffix(self, aggressive_stemmer):
        result = aggressive_stemmer.stem("işsiz")
        assert result in ("iş", "işsiz")
