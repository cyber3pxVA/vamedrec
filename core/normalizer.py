"""
Medication Normalizer
Standardizes medication names, forms, strengths, routes, and frequencies.
Implements deterministic preprocessing logic.
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass
import config


@dataclass
class Medication:
    """Normalized medication structure."""
    raw_input: str
    name: str
    generic_name: str
    strength: Optional[str] = None
    form: Optional[str] = None
    route: Optional[str] = None
    frequency: Optional[str] = None
    instructions: Optional[str] = None
    normalized_dose: Optional[str] = None
    is_active: bool = True
    expiration_date: Optional[str] = None
    status: Optional[str] = None  # For ledger tracking


class MedicationNormalizer:
    """Handles medication normalization and standardization."""
    
    def __init__(self):
        self.brand_to_generic = config.BRAND_TO_GENERIC
        self.route_synonyms = config.ROUTE_SYNONYMS
        self.frequency_synonyms = config.FREQUENCY_SYNONYMS
    
    def normalize(self, med_string: str) -> Medication:
        """
        Normalize a medication string into structured format.
        
        Args:
            med_string: Raw medication string (e.g., "Tylenol 500mg tablet by mouth twice daily")
        
        Returns:
            Medication object with normalized fields
        """
        med_string = med_string.strip().lower()
        
        # Extract components using regex patterns
        name = self._extract_name(med_string)
        generic_name = self._to_generic(name)
        strength = self._extract_strength(med_string)
        form = self._extract_form(med_string)
        route = self._extract_route(med_string)
        frequency = self._extract_frequency(med_string)
        normalized_dose = self._normalize_dose(strength)
        
        return Medication(
            raw_input=med_string,
            name=name,
            generic_name=generic_name,
            strength=strength,
            form=form,
            route=route,
            frequency=frequency,
            normalized_dose=normalized_dose,
        )
    
    def normalize_batch(self, med_list: List[str]) -> List[Medication]:
        """Normalize a list of medications."""
        return [self.normalize(med) for med in med_list]
    
    def _extract_name(self, med_string: str) -> str:
        """Extract medication name (first word/words before strength)."""
        # Simple heuristic: name is before the first digit or common form word
        match = re.match(r'^([a-z\s\-]+?)(?:\s+\d|\s+tablet|\s+capsule|\s+$)', med_string)
        if match:
            return match.group(1).strip()
        
        # Fallback: first word
        return med_string.split()[0] if med_string else ""
    
    def _to_generic(self, name: str) -> str:
        """Convert brand name to generic if known."""
        name_lower = name.lower().strip()
        return self.brand_to_generic.get(name_lower, name_lower)
    
    def _extract_strength(self, med_string: str) -> Optional[str]:
        """Extract medication strength (e.g., '500mg', '10 mg', '½ 10mg')."""
        # Pattern: optional fraction + number + optional space + unit
        patterns = [
            r'(½\s*\d+\s*mg)',  # ½ 10mg
            r'(\d+\.?\d*\s*mg)',  # 500mg or 500 mg
            r'(\d+\.?\d*\s*mcg)',  # mcg
            r'(\d+\.?\d*\s*ml)',  # ml
            r'(\d+\.?\d*\s*%)',  # percentage
            r'(\d+\.?\d*\s*units?)',  # units
        ]
        
        for pattern in patterns:
            match = re.search(pattern, med_string)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _normalize_dose(self, strength: Optional[str]) -> Optional[str]:
        """
        Normalize dose calculations (e.g., '½ 10mg' -> '5mg').
        Preserves original instruction semantics.
        """
        if not strength:
            return None
        
        # Handle fraction notation
        if '½' in strength:
            match = re.search(r'½\s*(\d+\.?\d*)\s*(mg|mcg|ml)', strength)
            if match:
                value = float(match.group(1)) / 2
                unit = match.group(2)
                return f"{value}{unit}"
        
        return strength
    
    def _extract_form(self, med_string: str) -> Optional[str]:
        """Extract medication form (tablet, capsule, etc.)."""
        forms = [
            'tablet', 'tab', 'capsule', 'cap', 'injection', 'solution',
            'cream', 'ointment', 'gel', 'patch', 'inhaler', 'drops'
        ]
        
        for form in forms:
            if form in med_string:
                return form
        
        return None
    
    def _extract_route(self, med_string: str) -> Optional[str]:
        """Extract and standardize route of administration."""
        for synonym, standard in self.route_synonyms.items():
            if synonym in med_string:
                return standard
        
        # Direct match on standard routes
        routes = ['po', 'iv', 'im', 'sq', 'topical', 'inhaled']
        for route in routes:
            if route in med_string:
                return route
        
        return None
    
    def _extract_frequency(self, med_string: str) -> Optional[str]:
        """Extract and standardize frequency."""
        for synonym, standard in self.frequency_synonyms.items():
            if synonym in med_string:
                return standard
        
        # Direct match on standard frequencies
        frequencies = ['daily', 'twice daily', 'three times daily', 'prn', 'as needed']
        for freq in frequencies:
            if freq in med_string:
                return freq
        
        return None
    
    def check_equivalence(self, med1: Medication, med2: Medication) -> bool:
        """
        Check if two medications are equivalent considering dose adjustments.
        
        Returns:
            True if medications are the same drug with equivalent dosing
        """
        # Must be same generic drug
        if med1.generic_name != med2.generic_name:
            return False
        
        # Must be same route
        if med1.route != med2.route:
            return False
        
        # Check if normalized doses are equivalent
        if med1.normalized_dose == med2.normalized_dose:
            return True
        
        # Additional logic could check daily total doses, etc.
        return False
    
    def tag_directionality(
        self,
        baseline_list: List[Medication],
        reference_list: List[Medication],
        baseline_label: str = "now",
        reference_label: str = "then"
    ) -> Dict[str, List[Medication]]:
        """
        Tag medication lists with directionality labels.
        
        Args:
            baseline_list: The "now" list (e.g., inpatient on admission)
            reference_list: The "then" list (e.g., outpatient home meds)
            baseline_label: Label for baseline (default: "now")
            reference_label: Label for reference (default: "then")
        
        Returns:
            Dictionary with tagged lists
        """
        for med in baseline_list:
            med.status = f"{baseline_label}"
        
        for med in reference_list:
            med.status = f"{reference_label}"
        
        return {
            baseline_label: baseline_list,
            reference_label: reference_list
        }
