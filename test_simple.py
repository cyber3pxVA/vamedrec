"""
Simple test of the med rec pipeline without spaCy dependency.
"""

import sys
sys.path.insert(0, '.')

from core.clinical_extractor import ClinicalExtractor
from models.med_event import MedicationEvent

# Test clinical extractor
print("\n" + "=" * 80)
print("Testing Clinical Extractor (Regex Fallback)")
print("=" * 80)

extractor = ClinicalExtractor()

test_text = """
Current Medications:
1. Metformin 500mg PO BID - for diabetes
2. Lisinopril 10mg PO daily - for hypertension
3. Patient stopped taking Aspirin 81mg daily
4. Atorvastatin 20mg PO QHS
"""

print(f"\nInput text:\n{test_text}")

meds = extractor.extract_medications(test_text, "current")

print(f"\n✓ Extracted {len(meds)} medications:")

for med in meds:
    print(f"\n  - {med.drug_name_norm}")
    print(f"    Dose: {med.dose_strength}{med.dose_unit}")
    print(f"    Frequency: {med.frequency}")
    print(f"    Route: {med.route}")
    print(f"    Negated: {med.is_negated}")
    print(f"    Method: {med.extraction_method}")

print("\n" + "=" * 80)
print("Test Complete!")
print("=" * 80)
