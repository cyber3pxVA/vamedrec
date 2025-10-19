"""
Medication Reconciliation Pipeline
Orchestrates the three-stage reconciliation process.
"""

from typing import Dict, Tuple, List
from models.med_event import MedicationEvent, MedicationList
from core.clinical_extractor import ClinicalExtractor
from core.temporal_parser import TemporalParser
from core.med_normalizer import MedicationNormalizer
from core.reconciliation_engine import ReconciliationEngine
from core.report_generator import ReportGenerator
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedRecPipeline:
    """
    End-to-end medication reconciliation pipeline.
    
    Three-Stage Process:
    1. Stage 1: Deterministic extraction (medSpaCy + Duckling)
    2. Stage 2: Data normalization (RxNorm/UMLS)
    3. Stage 3: LLM-powered reconciliation
    """
    
    def __init__(self):
        """Initialize all pipeline components."""
        logger.info("Initializing MedRecPipeline")
        
        # Stage 1: Extraction
        self.clinical_extractor = ClinicalExtractor()
        self.temporal_parser = TemporalParser()
        
        # Stage 2: Normalization
        self.normalizer = MedicationNormalizer()
        
        # Stage 3: Reconciliation
        self.reconciliation_engine = ReconciliationEngine()
        self.report_generator = ReportGenerator()
        
        logger.info("MedRecPipeline initialized successfully")
    
    def run_full_pipeline(
        self,
        prior_text: str,
        current_text: str,
        patient_id: str = None,
        encounter_id: str = None,
        prior_text_source: str = "Prior Medication List",
        current_text_source: str = "Current Clinical Note"
    ) -> Dict:
        """
        Run the complete medication reconciliation pipeline.
        
        Args:
            prior_text: Prior/home medication list as free text
            current_text: Current medication notes as free text
            patient_id: Optional patient identifier
            encounter_id: Optional encounter identifier
            prior_text_source: Description of prior text source
            current_text_source: Description of current text source
        
        Returns:
            Complete reconciliation result with report
        """
        logger.info("=" * 80)
        logger.info("Starting Full Medication Reconciliation Pipeline")
        logger.info("=" * 80)
        
        # Stage 1: Extract medication events from both texts
        logger.info("\n[STAGE 1] Deterministic Extraction")
        logger.info("-" * 40)
        
        prior_meds, current_meds = self._stage1_extract(prior_text, current_text)
        
        logger.info(f"✓ Extracted {len(prior_meds)} prior medications")
        logger.info(f"✓ Extracted {len(current_meds)} current medications")
        
        # Stage 2: Normalize medication data
        logger.info("\n[STAGE 2] Data Normalization")
        logger.info("-" * 40)
        
        prior_meds_normalized, current_meds_normalized = self._stage2_normalize(
            prior_meds, current_meds
        )
        
        logger.info(f"✓ Normalized {len(prior_meds_normalized)} prior medications")
        logger.info(f"✓ Normalized {len(current_meds_normalized)} current medications")
        
        # Create MedicationList object
        med_list = MedicationList(
            patient_id=patient_id,
            encounter_id=encounter_id,
            reconciliation_date=datetime.utcnow(),
            medications=prior_meds_normalized + current_meds_normalized,
            prior_text_source=prior_text_source,
            current_text_source=current_text_source
        )
        
        # Stage 3: LLM-powered reconciliation
        logger.info("\n[STAGE 3] LLM-Powered Reconciliation")
        logger.info("-" * 40)
        
        reconciliation_result = self._stage3_reconcile(
            prior_meds_normalized,
            current_meds_normalized
        )
        
        logger.info(f"✓ Identified {reconciliation_result['summary']['matched_count']} matches")
        logger.info(f"✓ Identified {reconciliation_result['summary']['discrepancy_count']} discrepancies")
        logger.info(f"✓ Identified {reconciliation_result['summary']['addition_count']} additions")
        logger.info(f"✓ Identified {reconciliation_result['summary']['discontinuation_count']} discontinuations")
        logger.info(f"✓ Identified {reconciliation_result['summary']['ambiguity_count']} ambiguities")
          # Generate report
        logger.info("\n[REPORT GENERATION]")
        logger.info("-" * 40)
        
        markdown_report = self.report_generator.generate_report(reconciliation_result)
        html_report = self.report_generator.generate_html_report(reconciliation_result)
        
        logger.info("✓ Generated markdown report")
        logger.info("✓ Generated HTML report")
        
        # Compile final result
        final_result = {
            "medication_list": med_list.dict(),
            "reconciliation": reconciliation_result,
            "report_markdown": markdown_report,
            "report_html": html_report,
            "pipeline_metadata": {
                "pipeline_version": "1.0",
                "stages_completed": ["extraction", "normalization", "reconciliation"],
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        logger.info("\n" + "=" * 80)
        logger.info("Pipeline Complete!")
        logger.info("=" * 80 + "\n")
        
        return final_result
    
    def _stage1_extract(
        self,
        prior_text: str,
        current_text: str
    ) -> Tuple[List[MedicationEvent], List[MedicationEvent]]:
        """
        Stage 1: Extract medication events using medSpaCy and Duckling.
        
        Args:
            prior_text: Prior medication text
            current_text: Current medication text
        
        Returns:
            Tuple of (prior_events, current_events)
        """
        # Extract medications from both texts
        prior_meds = self.clinical_extractor.extract_medications(
            prior_text,
            list_source="prior"
        )
        
        current_meds = self.clinical_extractor.extract_medications(
            current_text,
            list_source="current"
        )
        
        # Enhance with temporal information
        prior_meds = self._add_temporal_info(prior_meds, prior_text)
        current_meds = self._add_temporal_info(current_meds, current_text)
        
        return prior_meds, current_meds
    
    def _add_temporal_info(
        self,
        meds: List[MedicationEvent],
        full_text: str
    ) -> List[MedicationEvent]:
        """Add temporal information to medication events."""
        # Extract all temporal expressions from text
        temporal_info = self.temporal_parser.extract_temporal_info(full_text)
        
        # If we found temporal info, apply it to medications
        if temporal_info['date_iso']:
            for med in meds:
                # Check if the medication's text snippet contains temporal info
                med_temporal = self.temporal_parser.extract_temporal_info(
                    med.raw_text_snippet
                )
                
                if med_temporal['date_iso']:
                    med.date_of_change_iso = med_temporal['date_iso']
                    med.temporal_expression = med_temporal['temporal_expression']
        
        return meds
    
    def _stage2_normalize(
        self,
        prior_meds: List[MedicationEvent],
        current_meds: List[MedicationEvent]
    ) -> Tuple[List[MedicationEvent], List[MedicationEvent]]:
        """
        Stage 2: Normalize medication data.
        
        Args:
            prior_meds: Prior medication events
            current_meds: Current medication events
        
        Returns:
            Tuple of (normalized_prior, normalized_current)
        """
        prior_normalized = self.normalizer.normalize_medication_list(prior_meds)
        current_normalized = self.normalizer.normalize_medication_list(current_meds)
        
        return prior_normalized, current_normalized
    
    def _stage3_reconcile(
        self,
        prior_meds: List[MedicationEvent],
        current_meds: List[MedicationEvent]
    ) -> Dict:
        """
        Stage 3: LLM-powered reconciliation.
        
        Args:
            prior_meds: Normalized prior medications
            current_meds: Normalized current medications
        
        Returns:
            Reconciliation result dictionary
        """
        return self.reconciliation_engine.reconcile(prior_meds, current_meds)
    
    def run_extraction_only(
        self,
        text: str,
        list_source: str = "current"
    ) -> List[MedicationEvent]:
        """
        Run only Stage 1 extraction (for testing/debugging).
        
        Args:
            text: Clinical text
            list_source: "prior" or "current"
        
        Returns:
            List of extracted MedicationEvent objects
        """
        return self.clinical_extractor.extract_medications(text, list_source)
    
    def run_extraction_and_normalization(
        self,
        prior_text: str,
        current_text: str
    ) -> Tuple[List[MedicationEvent], List[MedicationEvent]]:
        """
        Run Stages 1 and 2 only (for testing/debugging).
        
        Args:
            prior_text: Prior medication text
            current_text: Current medication text
        
        Returns:
            Tuple of (normalized_prior, normalized_current)
        """
        prior_meds, current_meds = self._stage1_extract(prior_text, current_text)
        return self._stage2_normalize(prior_meds, current_meds)


# Example usage
if __name__ == "__main__":
    # Initialize pipeline
    pipeline = MedRecPipeline()
    
    # Example clinical text
    prior_text = """
    PRIOR MEDICATION LIST (Home Medications):
    1. Metformin 500mg tablet by mouth twice daily - for diabetes
    2. Lisinopril 10mg tablet by mouth once daily - for hypertension
    3. Aspirin 81mg tablet by mouth once daily - for cardiovascular protection
    4. Atorvastatin 20mg tablet by mouth at bedtime - for cholesterol
    """
    
    current_text = """
    CURRENT MEDICATIONS (From Clinic Visit 10/19/2025):
    
    Patient continues metformin 500mg PO BID for diabetes control.
    
    Increased lisinopril to 20mg PO daily due to elevated BP readings.
    
    Patient stopped taking aspirin 3 weeks ago due to GI upset.
    
    Continue atorvastatin 20mg QHS.
    
    Started insulin glargine 10 units subcutaneous at bedtime for better glycemic control.
    
    Patient mentioned he might start warfarin but we're still considering it.
    """
    
    # Run full pipeline
    result = pipeline.run_full_pipeline(
        prior_text=prior_text,
        current_text=current_text,
        patient_id="VA-12345678",
        encounter_id="ENC-2025-10-19-001"
    )
    
    # Print markdown report
    print("\n" + "=" * 80)
    print("RECONCILIATION REPORT")
    print("=" * 80 + "\n")
    print(result['report_markdown'])
    
    # Print JSON summary
    import json
    print("\n" + "=" * 80)
    print("JSON SUMMARY")
    print("=" * 80 + "\n")
    print(json.dumps(result['reconciliation']['summary'], indent=2))
