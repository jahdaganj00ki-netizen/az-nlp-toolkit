"""Tests for the Azerbaijani tokenizer."""

import pytest
from az_nlp.tokenizer import AzTokenizer


@pytest.fixture
def tokenizer():
    return AzTokenizer()


class TestWordTokenization:
    """Test word-level tokenization."""

    def test_basic_sentence(self, tokenizer):
        tokens = tokenizer.tokenize("Bakı gözəl şəhərdir.")
        assert tokens == ["Bakı", "gözəl", "şəhərdir", "."]

    def test_azerbaijani_characters(self, tokenizer):
        """All AZ-specific characters should be preserved."""
        text = "Çörək bişirmək üçün əməkdaşlığa ehtiyac var"
        tokens = tokenizer.tokenize(text)
        assert "Çörək" in tokens
        assert "üçün" in tokens
        assert "əməkdaşlığa" in tokens

    def test_abbreviations_with_dots(self, tokenizer):
        """Abbreviations should be kept as single tokens."""
        tokens = tokenizer.tokenize("Bakı şəh. daxilində 5 mln. manat")
        assert "şəh." in tokens
        assert "mln." in tokens

    def test_decimal_numbers(self, tokenizer):
        """Numbers with decimal points should be single tokens."""
        tokens = tokenizer.tokenize("Qiymət 1.5 mln. dollardır")
        assert "1.5" in tokens

    def test_comma_decimal(self, tokenizer):
        """Numbers with comma decimals (European style)."""
        tokens = tokenizer.tokenize("Çəki 3,14 kq-dır")
        assert "3,14" in tokens

    def test_empty_input(self, tokenizer):
        assert tokenizer.tokenize("") == []
        assert tokenizer.tokenize("   ") == []

    def test_punctuation_separation(self, tokenizer):
        tokens = tokenizer.tokenize("Salam! Necəsən?")
        assert "!" in tokens
        assert "?" in tokens

    def test_hyphenated_words(self, tokenizer):
        """Hyphenated words should stay together."""
        tokens = tokenizer.tokenize("sosial-iqtisadi inkişaf")
        assert "sosial-iqtisadi" in tokens

    def test_word_tokenize_no_punct(self, tokenizer):
        """word_tokenize should exclude punctuation."""
        words = tokenizer.word_tokenize("Bakı gözəl şəhərdir!")
        assert "!" not in words
        assert "Bakı" in words


class TestSentenceTokenization:
    """Test sentence-level tokenization."""

    def test_basic_sentences(self, tokenizer):
        text = "Birinci cümlə. İkinci cümlə."
        sents = tokenizer.sent_tokenize(text)
        assert len(sents) == 2
        assert sents[0] == "Birinci cümlə."

    def test_abbreviation_not_sentence_boundary(self, tokenizer):
        """Abbreviations should not split sentences."""
        text = "Bakı şəh. daxilində yük daşınıb. Yeni sifariş var."
        sents = tokenizer.sent_tokenize(text)
        assert len(sents) == 2
        assert "şəh." in sents[0]

    def test_question_exclamation(self, tokenizer):
        text = "Nə vaxt gəldi? Bilmirəm! Soruşaq."
        sents = tokenizer.sent_tokenize(text)
        assert len(sents) == 3

    def test_single_sentence(self, tokenizer):
        text = "Bu bir cümlədir"
        sents = tokenizer.sent_tokenize(text)
        assert len(sents) == 1

    def test_empty_input(self, tokenizer):
        assert tokenizer.sent_tokenize("") == []


class TestTokenizerOptions:
    """Test tokenizer configuration options."""

    def test_strip_abbreviation_dots(self):
        tokenizer = AzTokenizer(keep_abbrev_dots=False)
        tokens = tokenizer.tokenize("5 mln. manat")
        assert "mln" in tokens
        assert "mln." not in tokens
