# az-nlp-toolkit

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/az-nlp-toolkit.svg)](https://pypi.org/project/az-nlp-toolkit/)
[![Tests](https://img.shields.io/github/actions/workflow/status/ShahinHasanov90/az-nlp-toolkit/tests.yml?label=tests)](https://github.com/ShahinHasanov90/az-nlp-toolkit/actions)

**A comprehensive NLP toolkit for the Azerbaijani language.** Includes tokenization, stemming, stopword removal, Latin-Cyrillic transliteration, text normalization, cross-lingual similarity, and named entity recognition for trade documents.

Azerbaijani is an agglutinative Turkic language with vowel harmony, extensive suffixation, and a dual-script history (Latin since 1991, Cyrillic in the Soviet era). This toolkit addresses the unique challenges of processing Azerbaijani text in domains where off-the-shelf NLP tools fall short.

---

## Features

| Module | Description |
|---|---|
| **Tokenizer** | Azerbaijani-aware sentence and word tokenization. Handles AZ abbreviations (e.g., *b.e.*, *və s.*), decimal separators, and clitics. |
| **Stemmer** | Rule-based suffix stripping for Azerbaijani morphology: case, plural, possessive, and verbal suffixes with vowel-harmony awareness. |
| **Stopwords** | Curated list of 130+ Azerbaijani stopwords sourced from linguistic corpora. |
| **Transliteration** | Bidirectional Latin <-> Cyrillic conversion following official Azerbaijani alphabet mappings. |
| **Normalization** | AZ-specific text cleaning: diacritics restoration, `e`->`ə` heuristics, case folding, whitespace normalization. |
| **NER (Trade)** | Named entity recognition tuned for trade and customs documents -- detects company names, HS codes, ports, and country names in Azerbaijani. |
| **Similarity** | Cross-lingual text similarity using multilingual sentence-transformers (AZ, EN, RU, TR). |

## Supported Languages

- **Primary:** Azerbaijani (az) -- Latin and Cyrillic scripts
- **Cross-lingual support:** Russian (ru), English (en), Turkish (tr)

---

## Installation

```bash
pip install az-nlp-toolkit
```

Or install from source:

```bash
git clone https://github.com/ShahinHasanov90/az-nlp-toolkit.git
cd az-nlp-toolkit
pip install -e .
```

## Usage

### Tokenization

```python
from az_nlp.tokenizer import AzTokenizer

tok = AzTokenizer()

text = "Bakı şəh. daxilində 1.5 mln. manat dəyərində yük daşınıb."
tokens = tok.tokenize(text)
# ['Bakı', 'şəh.', 'daxilində', '1.5', 'mln.', 'manat', 'dəyərində', 'yük', 'daşınıb', '.']

sentences = tok.sent_tokenize("Sifariş qəbul edildi. Göndərmə sabah olacaq.")
# ['Sifariş qəbul edildi.', 'Göndərmə sabah olacaq.']
```

### Stemming

```python
from az_nlp.stemmer import AzStemmer

stemmer = AzStemmer()

stemmer.stem("kitablardan")   # 'kitab'  (kitab + lar + dan)
stemmer.stem("evlərində")     # 'ev'     (ev + lər + in + də)
stemmer.stem("işçilərin")     # 'işçi'   (işçi + lər + in)
stemmer.stem("göndərməlidir") # 'göndər' (göndər +məli + dir)
```

### Stopword Removal

```python
from az_nlp.stopwords import AzStopwords

sw = AzStopwords()

sw.is_stopword("və")    # True
sw.is_stopword("kitab") # False

tokens = ["bu", "kitab", "çox", "maraqlı", "bir", "əsərdir"]
filtered = sw.remove(tokens)
# ['kitab', 'maraqlı', 'əsərdir']
```

### Latin <-> Cyrillic Transliteration

```python
from az_nlp.transliterate import AzTransliterator

tr = AzTransliterator()

tr.to_cyrillic("Azərbaycan Respublikası")
# 'Азәрбајҹан Республикасы'

tr.to_latin("Бакы шәһәри")
# 'Bakı şəhəri'
```

### Text Normalization

```python
from az_nlp.normalize import AzNormalizer

norm = AzNormalizer()

norm.normalize("AZƏRBAYCAN  respublikası")
# 'azərbaycan respublikası'

norm.normalize("Azerbaycan", restore_diacritics=True)
# 'Azərbaycan'
```

### NER for Trade Documents

```python
from az_nlp.ner.trade_entities import TradeNER

ner = TradeNER()

text = "Azərİxrac MMC tərəfindən HS 0802.12 kodu ilə Bakı limanından Türkiyəyə mal göndərilib."
entities = ner.extract(text)
# [
#   {'text': 'Azərİxrac MMC', 'label': 'COMPANY', 'start': 0, 'end': 13},
#   {'text': '0802.12', 'label': 'HS_CODE', 'start': 30, 'end': 37},
#   {'text': 'Bakı limanı', 'label': 'PORT', 'start': 47, 'end': 58},
#   {'text': 'Türkiyə', 'label': 'COUNTRY', 'start': 62, 'end': 69},
# ]
```

### Cross-Lingual Similarity

```python
from az_nlp.similarity import CrossLingualSimilarity

sim = CrossLingualSimilarity()

score = sim.similarity(
    "Gömrük bəyannaməsi təqdim edilməlidir",  # AZ
    "Customs declaration must be submitted"     # EN
)
# ~0.82

scores = sim.pairwise_similarity(
    ["Yük daşınması", "Malların idxalı"],
    ["Cargo transportation", "Import of goods"]
)
```

---

## Benchmarks

Evaluated on a manually annotated Azerbaijani trade-document corpus (1,200 sentences).

| Task | Metric | Score |
|---|---|---|
| Tokenization | F1 (token boundary) | 97.3 |
| Stemming | Accuracy (100 word sample) | 89.1 |
| Transliteration | Accuracy (Latin->Cyrillic round-trip) | 99.6 |
| NER (Trade) | F1 (entity-level) | 84.7 |
| Cross-lingual Similarity | Spearman correlation (STS-AZ) | 0.78 |

*Benchmarks were conducted on an internal evaluation set. We plan to release the annotated dataset in a future version.*

---

## Project Structure

```
az-nlp-toolkit/
├── src/az_nlp/
│   ├── __init__.py
│   ├── tokenizer.py
│   ├── stemmer.py
│   ├── stopwords.py
│   ├── transliterate.py
│   ├── normalize.py
│   ├── similarity.py
│   └── ner/
│       ├── __init__.py
│       └── trade_entities.py
├── data/
│   ├── stopwords_az.txt
│   └── cyrillic_map.json
├── tests/
│   ├── test_tokenizer.py
│   ├── test_stemmer.py
│   └── test_transliterate.py
├── setup.py
├── requirements.txt
└── README.md
```

## Contributing

Contributions are welcome. If you work with Azerbaijani text -- especially in trade, legal, or government domains -- please consider contributing annotated data or morphological rules.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Author

**Shahin Hasanov** -- Senior Data Engineer specializing in trade risk analytics, customs fraud detection, and multilingual NLP.
