"""
Named Entity Recognition for Azerbaijani trade and customs documents.

Extracts:
  - COMPANY: Company names (MMC, ASC, QSC suffixes; known trade companies)
  - HS_CODE: Harmonized System commodity codes (4-10 digit, dotted)
  - PORT: Ports and terminals in Azerbaijan
  - COUNTRY: Country names in Azerbaijani
  - CURRENCY: Currency mentions
  - TRADE_TERM: Incoterms and trade terminology
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


@dataclass
class Entity:
    """A named entity extracted from text."""
    text: str
    label: str
    start: int
    end: int

    def to_dict(self) -> Dict:
        return asdict(self)


# --- Country names in Azerbaijani ---
_COUNTRIES_AZ: Dict[str, str] = {
    # Major trade partners of Azerbaijan
    "Azərbaycan": "AZ", "Türkiyə": "TR", "Rusiya": "RU",
    "Gürcüstan": "GE", "İran": "IR", "Qazaxıstan": "KZ",
    "Özbəkistan": "UZ", "Türkmənistan": "TM", "Ukrayna": "UA",
    "Almaniya": "DE", "İtaliya": "IT", "Fransa": "FR",
    "Böyük Britaniya": "GB", "İngiltərə": "GB",
    "ABŞ": "US", "Amerika Birləşmiş Ştatları": "US",
    "Çin": "CN", "Yaponiya": "JP", "Hindistan": "IN",
    "Braziliya": "BR", "Kanada": "CA", "Avstraliya": "AU",
    "İsrail": "IL", "Misir": "EG", "Səudiyyə Ərəbistanı": "SA",
    "BƏƏ": "AE", "Birləşmiş Ərəb Əmirlikləri": "AE",
    "Pakistan": "PK", "Əfqanıstan": "AF", "İraq": "IQ",
    "Polşa": "PL", "Rumıniya": "RO", "Bolqarıstan": "BG",
    "Yunanıstan": "GR", "İspaniya": "ES", "Portuqaliya": "PT",
    "Hollandiya": "NL", "Belçika": "BE", "İsveçrə": "CH",
    "Avstriya": "AT", "Çexiya": "CZ", "Macarıstan": "HU",
    "Finlandiya": "FI", "İsveç": "SE", "Norveç": "NO",
    "Danimarka": "DK", "Belarus": "BY", "Moldova": "MD",
    "Latviya": "LV", "Litva": "LT", "Estoniya": "EE",
    "Qırğızıstan": "KG", "Tacikistan": "TJ", "Monqolustan": "MN",
    "Cənubi Koreya": "KR", "İndoneziya": "ID",
    "Malayziya": "MY", "Tailand": "TH", "Vyetnam": "VN",
    "Sinqapur": "SG", "Filippin": "PH",
    "Argentina": "AR", "Meksika": "MX", "Kolumbiya": "CO",
    "Nigeriya": "NG", "Cənubi Afrika": "ZA",
}

# --- Ports and terminals ---
_PORTS_AZ = [
    "Bakı limanı", "Bakı Beynəlxalq Dəniz Ticarət Limanı",
    "Ələt limanı", "Ələt Beynəlxalq Dəniz Ticarət Limanı",
    "Astara limanı", "Lənkəran limanı",
    "Dubəndi terminalı", "Səngəçal terminalı",
    "Bakı neft terminalı", "Ceyhan limanı",
    "Supsa terminalı", "Batumi limanı",
    "Kulevi terminalı", "Poti limanı",
    # Short forms
    "Bakı limanından", "Ələt limanından",
]

# --- Company suffixes ---
_COMPANY_SUFFIXES = [
    "MMC",   # Məhdud Məsuliyyətli Cəmiyyət (LLC)
    "ASC",   # Açıq Səhmdar Cəmiyyəti (Open JSC)
    "QSC",   # Qapalı Səhmdar Cəmiyyəti (Closed JSC)
    "SC",    # Səhmdar Cəmiyyəti
    "İB",    # İctimai Birlik
    "MKB",   # Mərkəzi Kommersiya Bankı
]

# Known major trade-related companies in Azerbaijan
_KNOWN_COMPANIES = [
    "SOCAR", "ARDNŞ", "Azərbaycan Dəmir Yolları",
    "Azərbaycan Hava Yolları", "AzərSu",
    "Azərtexnolayn", "Azərİxrac",
]

# --- Incoterms and trade terms ---
_TRADE_TERMS = [
    "FOB", "CIF", "CFR", "EXW", "FCA", "CPT", "CIP",
    "DAP", "DPU", "DDP", "FAS",
    "gömrük bəyannaməsi", "idxal", "ixrac",
    "tranzit", "yenidən ixrac", "müvəqqəti idxal",
]

# --- Currency patterns ---
_CURRENCIES = {
    "AZN": "Azerbaijani Manat",
    "USD": "US Dollar",
    "EUR": "Euro",
    "RUB": "Russian Ruble",
    "TRY": "Turkish Lira",
    "GBP": "British Pound",
    "manat": "AZN",
    "dollar": "USD",
    "avro": "EUR",
    "rubl": "RUB",
    "lirə": "TRY",
}

# --- Regex patterns ---
# HS code: 4 to 10 digits, optionally separated by dots (e.g., 0802.12.00)
_HS_CODE_PATTERN = re.compile(
    r"\b(\d{4}(?:\.\d{2}(?:\.\d{2,4})?)?)\b"
)

# Company pattern: 1-4 capitalized words followed by a company suffix
_COMPANY_PATTERN = re.compile(
    r"((?:[A-ZÇƏĞİÖŞÜ][a-zçəğıöşü]+\s*){1,4}(?:"
    + "|".join(re.escape(s) for s in _COMPANY_SUFFIXES)
    + r"))\b"
)

# Currency amount pattern
_CURRENCY_AMOUNT_PATTERN = re.compile(
    r"\b(\d[\d\s,.]*)\s*("
    + "|".join(re.escape(c) for c in _CURRENCIES.keys())
    + r")\b",
    re.IGNORECASE,
)


class TradeNER:
    """Named Entity Recognition for Azerbaijani trade documents.

    Extracts companies, HS codes, ports, countries, currencies,
    and trade terms from Azerbaijani text.
    """

    def __init__(
        self,
        extra_companies: Optional[List[str]] = None,
        extra_countries: Optional[Dict[str, str]] = None,
    ):
        """
        Args:
            extra_companies: Additional company names to recognize.
            extra_countries: Additional country name -> ISO code mappings.
        """
        self._countries = _COUNTRIES_AZ.copy()
        if extra_countries:
            self._countries.update(extra_countries)

        self._known_companies = _KNOWN_COMPANIES.copy()
        if extra_companies:
            self._known_companies.extend(extra_companies)

        # Build country pattern (longer names first to match greedily)
        country_names = sorted(self._countries.keys(), key=len, reverse=True)
        self._country_pattern = re.compile(
            r"\b(" + "|".join(re.escape(c) for c in country_names) + r")\b"
        )

        # Build port pattern
        port_names = sorted(_PORTS_AZ, key=len, reverse=True)
        self._port_pattern = re.compile(
            r"(" + "|".join(re.escape(p) for p in port_names) + r")"
        )

        # Build known company pattern
        known = sorted(self._known_companies, key=len, reverse=True)
        self._known_company_pattern = re.compile(
            r"\b(" + "|".join(re.escape(c) for c in known) + r")\b"
        )

        # Build trade terms pattern
        terms = sorted(_TRADE_TERMS, key=len, reverse=True)
        self._trade_terms_pattern = re.compile(
            r"\b(" + "|".join(re.escape(t) for t in terms) + r")\b",
            re.IGNORECASE,
        )

    def extract(self, text: str) -> List[Dict]:
        """Extract all trade-related entities from text.

        Args:
            text: Input Azerbaijani text.

        Returns:
            List of entity dictionaries with keys:
                text, label, start, end.
        """
        if not text:
            return []

        entities: List[Entity] = []

        # Extract HS codes
        for m in _HS_CODE_PATTERN.finditer(text):
            code = m.group(1)
            # Validate: must have at least 4 digits total
            digits = code.replace(".", "")
            if len(digits) >= 4:
                entities.append(Entity(
                    text=code, label="HS_CODE",
                    start=m.start(1), end=m.end(1),
                ))

        # Extract companies (pattern-based)
        for m in _COMPANY_PATTERN.finditer(text):
            entities.append(Entity(
                text=m.group(1).strip(), label="COMPANY",
                start=m.start(1), end=m.end(1),
            ))

        # Extract known companies
        for m in self._known_company_pattern.finditer(text):
            # Avoid duplicates with pattern-based extraction
            if not any(
                e.start <= m.start() < e.end or e.start < m.end() <= e.end
                for e in entities
            ):
                entities.append(Entity(
                    text=m.group(1), label="COMPANY",
                    start=m.start(1), end=m.end(1),
                ))

        # Extract ports
        for m in self._port_pattern.finditer(text):
            entities.append(Entity(
                text=m.group(1), label="PORT",
                start=m.start(1), end=m.end(1),
            ))

        # Extract countries
        for m in self._country_pattern.finditer(text):
            # Skip if inside a port mention
            if not any(
                e.label == "PORT" and e.start <= m.start() and m.end() <= e.end
                for e in entities
            ):
                entities.append(Entity(
                    text=m.group(1), label="COUNTRY",
                    start=m.start(1), end=m.end(1),
                ))

        # Extract currencies
        for m in _CURRENCY_AMOUNT_PATTERN.finditer(text):
            entities.append(Entity(
                text=m.group(0).strip(), label="CURRENCY",
                start=m.start(), end=m.end(),
            ))

        # Extract trade terms
        for m in self._trade_terms_pattern.finditer(text):
            entities.append(Entity(
                text=m.group(1), label="TRADE_TERM",
                start=m.start(1), end=m.end(1),
            ))

        # Sort by position and deduplicate overlapping entities
        entities.sort(key=lambda e: (e.start, -e.end))
        entities = self._resolve_overlaps(entities)

        return [e.to_dict() for e in entities]

    def extract_companies(self, text: str) -> List[Dict]:
        """Extract only company entities."""
        return [e for e in self.extract(text) if e["label"] == "COMPANY"]

    def extract_hs_codes(self, text: str) -> List[Dict]:
        """Extract only HS code entities."""
        return [e for e in self.extract(text) if e["label"] == "HS_CODE"]

    def extract_countries(self, text: str) -> List[Dict]:
        """Extract only country entities."""
        return [e for e in self.extract(text) if e["label"] == "COUNTRY"]

    @staticmethod
    def _resolve_overlaps(entities: List[Entity]) -> List[Entity]:
        """Remove overlapping entities, keeping the longest match."""
        if not entities:
            return entities

        resolved = [entities[0]]
        for entity in entities[1:]:
            prev = resolved[-1]
            # If current entity overlaps with previous, keep the longer one
            if entity.start < prev.end:
                if (entity.end - entity.start) > (prev.end - prev.start):
                    resolved[-1] = entity
            else:
                resolved.append(entity)
        return resolved
