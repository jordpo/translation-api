import os
from typing import Dict

# Model configuration
MODEL_NAME = os.getenv("MODEL_NAME", "facebook/nllb-200-distilled-600M")

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour default

# Language codes mapping (common languages)
# NLLB uses ISO 639-3 codes with script suffixes
LANGUAGE_CODES: Dict[str, str] = {
    "en": "eng_Latn",  # English
    "es": "spa_Latn",  # Spanish
    "fr": "fra_Latn",  # French
    "de": "deu_Latn",  # German
    "it": "ita_Latn",  # Italian
    "pt": "por_Latn",  # Portuguese
    "ru": "rus_Cyrl",  # Russian
    "zh": "zho_Hans",  # Chinese (Simplified)
    "ja": "jpn_Jpan",  # Japanese
    "ko": "kor_Hang",  # Korean
    "ar": "arb_Arab",  # Arabic
    "hi": "hin_Deva",  # Hindi
    "nl": "nld_Latn",  # Dutch
    "pl": "pol_Latn",  # Polish
    "tr": "tur_Latn",  # Turkish
    "vi": "vie_Latn",  # Vietnamese
    "th": "tha_Thai",  # Thai
    "sv": "swe_Latn",  # Swedish
    "cs": "ces_Latn",  # Czech
    "el": "ell_Grek",  # Greek
}

# Supported languages for the API
SUPPORTED_LANGUAGES = list(LANGUAGE_CODES.keys())