"""
Clinical Entity Extractor (Stage 1)
Uses medSpaCy to extract medications and clinical context from free text.
Falls back to regex-based extraction if spaCy is not available.
"""

from typing import List, Dict, Optional, Tuple
from models.med_event import MedicationEvent
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClinicalExtractor:
    """
    Stage 1: Deterministic extraction of clinical entities using medSpaCy.
    
    Extracts:
    - Drug names (with RxNorm/UMLS mapping)
    - Dosing information (strength, unit, form)
    - Frequency and route
    - Clinical context (negation, historical, family history)
    """
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize the clinical extractor with medSpaCy pipeline.
        
        Args:
            model_name: spaCy model to use as base
        """
        logger.info(f"Initializing ClinicalExtractor with model: {model_name}")
        
        self.use_spacy = False
        self.nlp = None
        
        try:
            # Try to load spaCy model
            import spacy
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model: {model_name}")
            
            # Add medSpaCy components
            self._add_medspacy_components()
            self.use_spacy = True
            
        except (ImportError, OSError) as e:
            logger.warning(f"spaCy/medSpaCy not available: {e}")
            logger.warning("Falling back to regex-based extraction")
            self.use_spacy = False
        
        logger.info("ClinicalExtractor initialized successfully")
    
    def _add_medspacy_components(self):
        """Add medSpaCy pipeline components for clinical NLP."""
        try:
            import medspacy
            from medspacy.context import ConTextComponent
            from medspacy.section_detection import Sectionizer
            
            # Add context detector for negation, historical, family history
            context = ConTextComponent(
                self.nlp,
                rules="default",
                add_attrs=True
            )
            self.nlp.add_pipe(context)
            logger.info("Added ConText component for clinical context detection")
            
            # Add section detection
            sectionizer = Sectionizer(self.nlp, patterns="default")
            self.nlp.add_pipe(sectionizer)
            logger.info("Added Sectionizer component")
              # Add custom medication matcher
            self._add_medication_patterns()
            
        except ImportError:
            logger.warning("medSpaCy not installed. Using regex-based fallback")
            self.use_spacy = False
        except Exception as e:
            logger.warning(f"Error adding medSpaCy components: {e}")
            self.use_spacy = False
    
    def _add_medication_patterns(self):
        """Add custom patterns for medication entity recognition."""
        if not self.nlp:
            return
            
        try:
            from spacy.matcher import Matcher
            matcher = Matcher(self.nlp.vocab)
        except ImportError:
            return
        
        # Pattern for common medication formats
        # Example: "Metformin 500mg", "Aspirin 81 mg tablet"
        patterns = [
            # Drug + Dose + Unit
            [
                {"ENT_TYPE": "DRUG", "OP": "?"},
                {"LIKE_NUM": True},
                {"LOWER": {"IN": ["mg", "mcg", "g", "ml", "units", "iu"]}}
            ],
            # Drug + Dose + Unit + Form
            [
                {"ENT_TYPE": "DRUG", "OP": "?"},
                {"LIKE_NUM": True},
                {"LOWER": {"IN": ["mg", "mcg", "g", "ml", "units", "iu"]}},
                {"LOWER": {"IN": ["tablet", "capsule", "injection", "solution"]}}
            ],
        ]
        
        matcher.add("MEDICATION_PATTERN", patterns)
        self.medication_matcher = matcher
    
    def extract_medications(
        self,
        text: str,
        list_source: str = "current"
    ) -> List[MedicationEvent]:
        """
        Extract medication events from clinical text.
        
        Args:
            text: Raw clinical text
            list_source: "prior" or "current"
        
        Returns:
            List of MedicationEvent objects
        """
        logger.info(f"Extracting medications from {list_source} text ({len(text)} chars)")
        
        if self.use_spacy and self.nlp:
            # Use spaCy/medSpaCy pipeline
            return self._extract_with_spacy(text, list_source)
        else:
            # Use regex-based fallback
            return self._extract_with_regex(text, list_source)
    
    def _extract_with_spacy(self, text: str, list_source: str) -> List[MedicationEvent]:
        """Extract medications using spaCy pipeline."""
        # Process text with spaCy+medSpaCy pipeline
        doc = self.nlp(text)
        
        medication_events = []
        
        # Extract entities
        for ent in doc.ents:
            if self._is_medication_entity(ent):
                med_event = self._create_medication_event(
                    ent,
                    doc,
                    list_source                )
                if med_event:
                    medication_events.append(med_event)
        
        logger.info(f"Extracted {len(medication_events)} medication events")
        return medication_events
    
    def _extract_with_regex(self, text: str, list_source: str) -> List[MedicationEvent]:
        """Extract medications using regex patterns (fallback method)."""
        import re
        
        medication_events = []
        
        # Common medication pattern: drug name + dose + unit + frequency
        # Example: "Metformin 500mg PO BID"
        # Look for: capitalized drug name followed immediately by dose
        med_pattern = r'\b([A-Z][a-z]+(?:ol|in|il|ax|ex|pril|statin|formin|cycline|cillin|azole|zepam|oprazole)?)\s+(\d+(?:\.\d+)?)\s*(mg|mcg|g|ml|units?|iu)\s*(?:(PO|IV|IM|SQ|subq|oral|by mouth)\s+)?([A-Z]+|once|twice|three times|daily|nightly|at bedtime)?'
        
        # Split text into sentences
        sentences = text.split('\n')
        
        for sent in sentences:
            # Check for negation markers in the sentence
            is_negated = any(marker in sent.lower() for marker in [
                'stopped', 'discontinued', 'no longer', 'd/c', 'dc', 
                'stopped taking', 'quit', 'ceased'
            ])
            is_uncertain = any(marker in sent.lower() for marker in [
                'might', 'maybe', 'considering', 'possible', 'possibly',
                'may start', 'might start', 'consider'
            ])
            
            # Find medication matches
            matches = re.finditer(med_pattern, sent, re.IGNORECASE)
            
            for match in matches:
                drug_name = match.group(1).strip()
                dose_strength = float(match.group(2))
                dose_unit = match.group(3).lower()
                route = match.group(4).lower() if match.group(4) else None
                frequency = match.group(5) if match.group(5) else None
                
                # Create medication event
                med_event = MedicationEvent(
                    list_source=list_source,
                    drug_name_norm=drug_name.lower(),
                    drug_name_raw=drug_name,
                    dose_strength=dose_strength,
                    dose_unit=dose_unit,
                    frequency=frequency,
                    route=route,
                    is_negated=is_negated,
                    is_uncertain=is_uncertain,
                    raw_text_snippet=sent.strip(),
                    sentence_context=sent.strip(),
                    extraction_confidence=0.7,  # Lower confidence for regex
                    extraction_method="regex_fallback"
                )
                
                medication_events.append(med_event)
        
        logger.info(f"Extracted {len(medication_events)} medication events (regex)")
        return medication_events
    
    def _is_medication_entity(self, ent) -> bool:
        """Check if entity is a medication."""
        # Check if entity type suggests medication
        medication_labels = ["DRUG", "MEDICATION", "CHEMICAL", "TREATMENT"]
        return ent.label_ in medication_labels
    
    def _create_medication_event(
        self,
        ent,
        doc,
        list_source: str
    ) -> Optional[MedicationEvent]:
        """
        Create a MedicationEvent from a spaCy entity.
        
        Args:
            ent: spaCy entity
            doc: spaCy Doc object
            list_source: "prior" or "current"
        
        Returns:
            MedicationEvent or None
        """
        try:
            # Extract drug name
            drug_name_raw = ent.text
            drug_name_norm = drug_name_raw.lower().strip()
            
            # Get sentence context
            sent = ent.sent
            raw_text_snippet = sent.text
            
            # Extract dosing information
            dose_info = self._extract_dose_info(ent, sent)
            
            # Extract frequency and route
            frequency = self._extract_frequency(sent)
            route = self._extract_route(sent)
            
            # Get clinical context (negation, historical, etc.)
            context_flags = self._extract_context(ent)
            
            # Check for uncertainty markers
            is_uncertain = self._check_uncertainty(sent)
            
            # Create medication event
            med_event = MedicationEvent(
                list_source=list_source,
                drug_name_norm=drug_name_norm,
                drug_name_raw=drug_name_raw,
                dose_strength=dose_info.get("strength"),
                dose_unit=dose_info.get("unit"),
                form=dose_info.get("form"),
                frequency=frequency,
                route=route,
                is_negated=context_flags.get("is_negated", False),
                is_historical=context_flags.get("is_historical", False),
                is_family_history=context_flags.get("is_family_history", False),
                is_uncertain=is_uncertain,
                raw_text_snippet=raw_text_snippet,
                sentence_context=str(sent),
                extraction_confidence=ent._.get("confidence", 0.8),
                extraction_method="medspacy"
            )
            
            return med_event
            
        except Exception as e:
            logger.error(f"Error creating medication event: {e}")
            return None
    
    def _extract_dose_info(self, ent, sent) -> Dict[str, Optional[str]]:
        """Extract dosing information (strength, unit, form)."""
        import re
        
        # Look for dose pattern: number + unit
        dose_pattern = r'(\d+(?:\.\d+)?)\s*(mg|mcg|g|ml|units|iu|%)'
        matches = re.finditer(dose_pattern, sent.text, re.IGNORECASE)
        
        dose_info = {
            "strength": None,
            "unit": None,
            "form": None
        }
        
        for match in matches:
            dose_info["strength"] = float(match.group(1))
            dose_info["unit"] = match.group(2).lower()
            break  # Take first match
        
        # Look for form
        forms = ["tablet", "capsule", "injection", "solution", "cream", "patch", "inhaler"]
        for form in forms:
            if form in sent.text.lower():
                dose_info["form"] = form
                break
        
        return dose_info
    
    def _extract_frequency(self, sent) -> Optional[str]:
        """Extract frequency from sentence."""
        import re
        
        # Common frequency patterns
        freq_patterns = [
            r'\b(QD|BID|TID|QID|QHS|PRN|Q\d+H)\b',  # Abbreviations
            r'\b(once|twice|three times|four times)\s+(daily|a day|per day)\b',
            r'\b(every)\s+(\d+)\s+(hours?|days?)\b',
            r'\b(daily|nightly|weekly|monthly)\b'
        ]
        
        for pattern in freq_patterns:
            match = re.search(pattern, sent.text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_route(self, sent) -> Optional[str]:
        """Extract route of administration."""
        routes = {
            "po": ["po", "by mouth", "oral", "orally"],
            "iv": ["iv", "intravenous", "intravenously"],
            "im": ["im", "intramuscular"],
            "sq": ["sq", "subq", "subcutaneous", "subcutaneously"],
            "topical": ["topical", "topically"],
            "inhaled": ["inhaled", "inhalation"],
            "rectal": ["rectal", "rectally", "pr"],
            "sublingual": ["sublingual", "sl"]
        }
        
        sent_lower = sent.text.lower()
        for route_key, variants in routes.items():
            if any(variant in sent_lower for variant in variants):
                return route_key
        
        return None
    
    def _extract_context(self, ent) -> Dict[str, bool]:
        """Extract clinical context flags using medSpaCy ConText."""
        context_flags = {
            "is_negated": False,
            "is_historical": False,
            "is_family_history": False
        }
        
        # Check if entity has context attributes (from ConText component)
        if hasattr(ent._, "is_negated"):
            context_flags["is_negated"] = ent._.is_negated
        if hasattr(ent._, "is_historical"):
            context_flags["is_historical"] = ent._.is_historical
        if hasattr(ent._, "is_family"):
            context_flags["is_family_history"] = ent._.is_family
        
        return context_flags
    
    def _check_uncertainty(self, sent) -> bool:
        """Check if sentence contains uncertainty markers."""
        uncertainty_markers = [
            "might", "maybe", "possibly", "consider", "considering",
            "perhaps", "uncertain", "unclear", "may be", "could be",
            "likely", "unlikely", "probably", "seems", "appears"
        ]
        
        sent_lower = sent.text.lower()
        return any(marker in sent_lower for marker in uncertainty_markers)
    
    def process_text_pair(
        self,
        prior_text: str,
        current_text: str
    ) -> Tuple[List[MedicationEvent], List[MedicationEvent]]:
        """
        Process both prior and current texts.
        
        Args:
            prior_text: Prior medication list text
            current_text: Current medication notes text
        
        Returns:
            Tuple of (prior_events, current_events)
        """
        prior_events = self.extract_medications(prior_text, list_source="prior")
        current_events = self.extract_medications(current_text, list_source="current")
        
        return prior_events, current_events


# Example usage and testing
if __name__ == "__main__":
    # Test the extractor
    extractor = ClinicalExtractor()
    
    test_text = """
    Current Medications:
    1. Metformin 500mg PO BID - for diabetes
    2. Lisinopril 10mg PO daily - for hypertension
    3. Patient stopped taking aspirin 81mg 3 weeks ago
    4. We might start insulin glargine 10 units subcutaneous QHS
    """
    
    events = extractor.extract_medications(test_text, "current")
    
    print(f"\nExtracted {len(events)} medication events:")
    for event in events:
        print(f"\n- {event.drug_name_norm}")
        print(f"  Dose: {event.dose_strength}{event.dose_unit}")
        print(f"  Frequency: {event.frequency}")
        print(f"  Negated: {event.is_negated}")
        print(f"  Uncertain: {event.is_uncertain}")
