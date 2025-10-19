"""
Medication Normalizer (Stage 2)
Normalizes medication names using RxNorm/UMLS and standardizes attributes.
"""

import re
from typing import Optional, Dict, List
from models.med_event import MedicationEvent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedicationNormalizer:
    """
    Stage 2: Normalize medication data to standardized formats.
    
    Performs:
    - RxNorm/UMLS concept mapping (via QuickUMLS or external API)
    - Drug name normalization (brand -> generic)
    - Dose unit standardization
    - Route standardization
    - Frequency normalization
    """
    
    def __init__(self, use_quickumls: bool = False):
        """
        Initialize the medication normalizer.
        
        Args:
            use_quickumls: Whether to use QuickUMLS for concept mapping
        """
        logger.info("Initializing MedicationNormalizer")
        
        self.use_quickumls = use_quickumls
        self.quickumls_matcher = None
        
        if use_quickumls:
            try:
                from quickumls import QuickUMLS
                # Initialize QuickUMLS (requires downloaded UMLS data)
                self.quickumls_matcher = QuickUMLS(
                    quickumls_fp="/path/to/quickumls/data",
                    overlapping_criteria="score",
                    threshold=0.7
                )
                logger.info("QuickUMLS initialized")
            except Exception as e:
                logger.warning(f"QuickUMLS not available: {e}")
                self.use_quickumls = False
        
        # Brand to generic mappings
        self.brand_to_generic = {
            "tylenol": "acetaminophen",
            "motrin": "ibuprofen",
            "advil": "ibuprofen",
            "lasix": "furosemide",
            "glucophage": "metformin",
            "lipitor": "atorvastatin",
            "zocor": "simvastatin",
            "norvasc": "amlodipine",
            "prilosec": "omeprazole",
            "nexium": "esomeprazole",
            "prozac": "fluoxetine",
            "zoloft": "sertraline",
            "synthroid": "levothyroxine",
            "coumadin": "warfarin",
            "plavix": "clopidogrel",
        }
        
        # Common abbreviations and their full forms
        self.dose_unit_normalization = {
            "g": "gram",
            "mg": "milligram",
            "mcg": "microgram",
            "ml": "milliliter",
            "l": "liter",
            "iu": "international_unit",
            "u": "unit",
        }
        
        # Route normalization
        self.route_normalization = {
            "po": "oral",
            "by mouth": "oral",
            "orally": "oral",
            "iv": "intravenous",
            "intravenous": "intravenous",
            "im": "intramuscular",
            "intramuscular": "intramuscular",
            "sq": "subcutaneous",
            "subq": "subcutaneous",
            "subcutaneous": "subcutaneous",
            "sl": "sublingual",
            "sublingual": "sublingual",
            "pr": "rectal",
            "rectal": "rectal",
            "topical": "topical",
            "inhaled": "inhalation",
            "inhalation": "inhalation",
        }
        
        # Frequency normalization
        self.frequency_normalization = {
            "qd": "once_daily",
            "daily": "once_daily",
            "once daily": "once_daily",
            "bid": "twice_daily",
            "twice daily": "twice_daily",
            "tid": "three_times_daily",
            "three times daily": "three_times_daily",
            "qid": "four_times_daily",
            "four times daily": "four_times_daily",
            "qhs": "at_bedtime",
            "at bedtime": "at_bedtime",
            "qam": "in_morning",
            "prn": "as_needed",
            "as needed": "as_needed",
            "q4h": "every_4_hours",
            "q6h": "every_6_hours",
            "q8h": "every_8_hours",
            "q12h": "every_12_hours",
        }
        
        logger.info("MedicationNormalizer initialized")
    
    def normalize_medication(self, med_event: MedicationEvent) -> MedicationEvent:
        """
        Normalize a medication event.
        
        Args:
            med_event: Raw MedicationEvent from extraction
        
        Returns:
            Normalized MedicationEvent
        """
        # Normalize drug name
        med_event.drug_name_norm = self._normalize_drug_name(med_event.drug_name_norm)
        
        # Attempt RxNorm/UMLS mapping
        if self.use_quickumls:
            rxnorm_cui = self._get_rxnorm_cui(med_event.drug_name_norm)
            if rxnorm_cui:
                med_event.rxnorm_cui = rxnorm_cui
        
        # Normalize dose unit
        if med_event.dose_unit:
            med_event.dose_unit = self._normalize_dose_unit(med_event.dose_unit)
        
        # Normalize route
        if med_event.route:
            med_event.route = self._normalize_route(med_event.route)
        
        # Normalize frequency
        if med_event.frequency:
            med_event.frequency = self._normalize_frequency(med_event.frequency)
        
        return med_event
    
    def normalize_medication_list(
        self,
        med_events: List[MedicationEvent]
    ) -> List[MedicationEvent]:
        """
        Normalize a list of medication events.
        
        Args:
            med_events: List of raw MedicationEvent objects
        
        Returns:
            List of normalized MedicationEvent objects
        """
        return [self.normalize_medication(med) for med in med_events]
    
    def _normalize_drug_name(self, drug_name: str) -> str:
        """
        Normalize drug name (brand -> generic, lowercase, clean).
        
        Args:
            drug_name: Raw drug name
        
        Returns:
            Normalized drug name
        """
        # Convert to lowercase
        name_lower = drug_name.lower().strip()
        
        # Remove extra whitespace
        name_clean = re.sub(r'\s+', ' ', name_lower)
        
        # Check brand-to-generic mapping
        if name_clean in self.brand_to_generic:
            return self.brand_to_generic[name_clean]
        
        return name_clean
    
    def _normalize_dose_unit(self, unit: str) -> str:
        """
        Normalize dose unit.
        
        Args:
            unit: Raw dose unit
        
        Returns:
            Normalized dose unit
        """
        unit_lower = unit.lower().strip()
        
        if unit_lower in self.dose_unit_normalization:
            return self.dose_unit_normalization[unit_lower]
        
        return unit_lower
    
    def _normalize_route(self, route: str) -> str:
        """
        Normalize route of administration.
        
        Args:
            route: Raw route
        
        Returns:
            Normalized route
        """
        route_lower = route.lower().strip()
        
        if route_lower in self.route_normalization:
            return self.route_normalization[route_lower]
        
        return route_lower
    
    def _normalize_frequency(self, frequency: str) -> str:
        """
        Normalize frequency.
        
        Args:
            frequency: Raw frequency
        
        Returns:
            Normalized frequency
        """
        freq_lower = frequency.lower().strip()
        
        if freq_lower in self.frequency_normalization:
            return self.frequency_normalization[freq_lower]
        
        return freq_lower
    
    def _get_rxnorm_cui(self, drug_name: str) -> Optional[str]:
        """
        Get RxNorm CUI for a drug name using QuickUMLS.
        
        Args:
            drug_name: Normalized drug name
        
        Returns:
            RxNorm CUI or None
        """
        if not self.quickumls_matcher:
            return None
        
        try:
            matches = self.quickumls_matcher.match(drug_name, best_match=True)
            
            if matches and len(matches) > 0:
                # Get the best match
                best_match = matches[0][0]
                return best_match['cui']
        
        except Exception as e:
            logger.error(f"Error getting RxNorm CUI: {e}")
        
        return None
    
    def get_drug_equivalence_score(
        self,
        drug1: str,
        drug2: str
    ) -> float:
        """
        Calculate equivalence score between two drug names.
        
        Args:
            drug1: First drug name
            drug2: Second drug name
        
        Returns:
            Equivalence score (0.0 to 1.0)
        """
        # Normalize both names
        name1 = self._normalize_drug_name(drug1)
        name2 = self._normalize_drug_name(drug2)
        
        # Exact match
        if name1 == name2:
            return 1.0
        
        # Check if one is a substring of the other
        if name1 in name2 or name2 in name1:
            return 0.8
        
        # Calculate simple string similarity (Levenshtein-like)
        similarity = self._string_similarity(name1, name2)
        
        return similarity
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """
        Calculate string similarity using simple character overlap.
        
        Args:
            s1: First string
            s2: Second string
        
        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not s1 or not s2:
            return 0.0
        
        # Convert to sets of characters
        set1 = set(s1)
        set2 = set(s2)
        
        # Calculate Jaccard similarity
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        if union == 0:
            return 0.0
        
        return intersection / union


# Example usage
if __name__ == "__main__":
    normalizer = MedicationNormalizer()
    
    # Test drug name normalization
    test_drugs = ["Tylenol", "LASIX", "metformin", "Lipitor"]
    
    print("\nDrug Name Normalization:")
    for drug in test_drugs:
        normalized = normalizer._normalize_drug_name(drug)
        print(f"{drug} -> {normalized}")
    
    # Test equivalence scoring
    print("\nEquivalence Scoring:")
    pairs = [
        ("Tylenol", "acetaminophen"),
        ("metformin", "metformin"),
        ("aspirin", "ibuprofen")
    ]
    
    for drug1, drug2 in pairs:
        score = normalizer.get_drug_equivalence_score(drug1, drug2)
        print(f"{drug1} vs {drug2}: {score:.2f}")
