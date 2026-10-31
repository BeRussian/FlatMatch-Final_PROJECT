"""
FlatMatch - Resilient Local Address Normalizer
===============================================
Zero-dependency, zero-API-key address text normalizer.
Cleans raw user input, expands common Israeli city and institution acronyms,
and safely preserves unfamiliar addresses without throwing errors.
"""

import re
from typing import Dict

# Common Israeli place, city, and institution aliases/acronyms
COMMON_ALIASES: Dict[str, str] = {
    'ת"א': "תל אביב",
    'תא': "תל אביב",
    'ר"ג': "רמת גן",
    'רג': "רמת גן",
    'ב"ש': "באר שבע",
    'בש': "באר שבע",
    'פ"ת': "פתח תקווה",
    'פת': "פתח תקווה",
    'ראשל"צ': "ראשון לציון",
    'ראשלצ': "ראשון לציון",
    'אונו': "הקריה האקדמית אונו, קרית אונו",
    'הקריה אונו': "הקריה האקדמית אונו, קרית אונו",
    'קרית אונו': "קרית אונו",
    'אוני תל אביב': "אוניברסיטת תל אביב",
    'אוני ת"א': "אוניברסיטת תל אביב",
    'טכניון': "הטכניון, חיפה",
    'עברית': "האוניברסיטה העברית, ירושלים",
    'בן גוריון': "אוניברסיטת בן-גוריון, באר שבע",
    'עזריאלי': "מרכז עזריאלי, תל אביב",
    'בורסה': "מתחם הבורסה, רמת גן",
}


def normalize_address(raw_text: str) -> str:
    """
    Cleans and standardizes raw address input safely.
    
    1. Strips leading/trailing whitespace and normalizes internal spaces.
    2. Matches known acronyms/aliases and replaces them.
    3. Safely preserves any general or unfamiliar address string as-is.
    """
    if not isinstance(raw_text, str) or not raw_text.strip():
        return "Center, Tel Aviv"

    cleaned = raw_text.strip()
    # Normalize multiple spaces into single space
    cleaned = re.sub(r"\s+", " ", cleaned)

    # Check exact match in alias dictionary (case-insensitive for english, trimmed for hebrew)
    cleaned_lower = cleaned.lower()
    for alias, replacement in COMMON_ALIASES.items():
        if cleaned_lower == alias.lower():
            return replacement

    # Word-level token replacement for common acronyms
    tokens = cleaned.split()
    replaced_tokens = []
    for token in tokens:
        token_clean = token.strip(",.-'\"")
        if token_clean in COMMON_ALIASES:
            replaced_tokens.append(COMMON_ALIASES[token_clean])
        else:
            replaced_tokens.append(token)

    return " ".join(replaced_tokens)


class AddressNormalizer:
    """Utility class encapsulating address normalization methods."""

    @staticmethod
    def normalize(raw_text: str) -> str:
        return normalize_address(raw_text)

