"""
VAMedRec - Centralized Configuration
All application settings, constants, and environment variables.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# LLM Configuration
# ============================================================================

# Azure OpenAI or OpenAI configuration
AZURE_ENDPOINT: str = os.getenv("AZURE_ENDPOINT", "")
LLM_ENDPOINT: str = os.getenv("LLM_ENDPOINT", os.getenv("AZURE_ENDPOINT", "https://api.openai.com/v1"))
LLM_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL: str = os.getenv("MODEL_NAME", os.getenv("LLM_MODEL", "gpt-4o"))
USE_AZURE: bool = bool(os.getenv("AZURE_ENDPOINT", ""))

# LLM parameters
LLM_TEMPERATURE: float = 0.1  # Low temperature for consistency
LLM_MAX_TOKENS: int = 4000
LLM_TIMEOUT: int = 60  # seconds

# ============================================================================
# Normalization Rules
# ============================================================================

# Generic name mappings (brand -> generic)
BRAND_TO_GENERIC = {
    "tylenol": "acetaminophen",
    "motrin": "ibuprofen",
    "advil": "ibuprofen",
    "lasix": "furosemide",
    "glucophage": "metformin",
}

# Route standardization
ROUTE_SYNONYMS = {
    "by mouth": "po",
    "oral": "po",
    "orally": "po",
    "intravenous": "iv",
    "intramuscular": "im",
    "subcutaneous": "sq",
    "subq": "sq",
}

# Frequency standardization
FREQUENCY_SYNONYMS = {
    "once daily": "daily",
    "qd": "daily",
    "once a day": "daily",
    "bid": "twice daily",
    "twice a day": "twice daily",
    "tid": "three times daily",
    "qid": "four times daily",
    "qhs": "at bedtime",
}

# ============================================================================
# Temporal Logic
# ============================================================================

# Recently expired medications (days)
RECENTLY_EXPIRED_THRESHOLD: int = 90  # TJC guideline

# ============================================================================
# Safety Check Thresholds
# ============================================================================

# Renal function (eGFR thresholds in mL/min/1.73m²)
EGFR_SEVERE_THRESHOLD: int = 30
EGFR_MODERATE_THRESHOLD: int = 60

# Contraindicated drugs by renal function
RENAL_CONTRAINDICATIONS = {
    "metformin": {"egfr_threshold": 30, "reason": "Lactic acidosis risk"},
    "nsaid": {"egfr_threshold": 30, "reason": "Acute kidney injury risk"},
    "dabigatran": {"egfr_threshold": 30, "reason": "Increased bleeding risk"},
}

# High-severity drug interactions (simplified examples)
HIGH_SEVERITY_INTERACTIONS = [
    {"drug1": "warfarin", "drug2": "nsaid", "risk": "Major bleeding"},
    {"drug1": "methotrexate", "drug2": "nsaid", "risk": "Methotrexate toxicity"},
    {"drug1": "ssri", "drug2": "maoi", "risk": "Serotonin syndrome"},
]

# Therapeutic classes for duplication detection
THERAPEUTIC_CLASSES = {
    "nsaid": ["ibuprofen", "naproxen", "ketorolac", "diclofenac"],
    "ssri": ["fluoxetine", "sertraline", "citalopram", "escitalopram"],
    "statin": ["atorvastatin", "simvastatin", "rosuvastatin", "pravastatin"],
    "ppi": ["omeprazole", "pantoprazole", "esomeprazole", "lansoprazole"],
}

# ============================================================================
# Data Source Configuration
# ============================================================================

# VA National Formulary (placeholder - would connect to actual database)
VA_FORMULARY_PATH: Optional[str] = os.getenv("VA_FORMULARY_PATH")

# ============================================================================
# Output Configuration
# ============================================================================

# Ledger status options
LEDGER_STATUSES = [
    "New",
    "Not Continued",
    "Changed",
    "Continued—No Change",
    "Unmatched—Verify",
]

# ============================================================================
# API Configuration
# ============================================================================

FLASK_HOST: str = "0.0.0.0"
FLASK_PORT: int = int(os.getenv("PORT", "5000"))
FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"

# ============================================================================
# Validation
# ============================================================================

def validate_config() -> None:
    """Validate required configuration is present."""
    if not LLM_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY environment variable is required. "
            "Set it in .env file or as environment variable."
        )
    print(f"✓ Configuration loaded successfully")
    print(f"  - LLM Model: {LLM_MODEL}")
    print(f"  - LLM Endpoint: {LLM_ENDPOINT}")
