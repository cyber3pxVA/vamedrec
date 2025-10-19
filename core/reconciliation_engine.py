"""
Reconciliation Engine (Stage 3)
LLM-powered medication reconciliation comparing prior and current medication lists.
"""

from typing import List, Dict, Optional, Tuple
from models.med_event import MedicationEvent, MedicationList
from core.model_engine import ModelEngine
from core.med_normalizer import MedicationNormalizer
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReconciliationEngine:
    """
    Stage 3: LLM-powered reconciliation comparing prior vs current medications.
    
    Performs:
    - Automated matching of equivalent medications
    - Detection of discrepancies (dose changes, discontinuations, additions)
    - Identification of ambiguities requiring human review
    - Generation of actionable reconciliation reports
    """
    
    def __init__(self):
        """Initialize the reconciliation engine."""
        logger.info("Initializing ReconciliationEngine")
        
        self.model_engine = ModelEngine()
        self.normalizer = MedicationNormalizer()
        
        # Load reconciliation prompt template
        self.prompt_template = self._load_prompt_template()
        
        logger.info("ReconciliationEngine initialized")
    
    def _load_prompt_template(self) -> str:
        """Load the LLM prompt template for reconciliation."""
        try:
            with open("prompts/reconciliation_prompt.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            logger.warning("Reconciliation prompt not found, using default")
            return self._get_default_prompt_template()
    
    def _get_default_prompt_template(self) -> str:
        """Default prompt template for reconciliation."""
        return """You are a clinical pharmacist performing medication reconciliation.

Your task is to compare a patient's PRIOR medication list with their CURRENT medication notes and identify:
1. **MATCHED**: Medications that appear in both lists (continuing unchanged or with minor variations)
2. **DISCREPANCIES**: Medications with changes in dose, frequency, route, or that were discontinued
3. **ADDITIONS**: New medications in the current list not present in the prior list
4. **DISCONTINUATIONS**: Medications from the prior list that are missing or explicitly stopped in current notes
5. **AMBIGUITIES**: Unclear situations requiring human pharmacist review

# PRIOR MEDICATIONS
{prior_meds_json}

# CURRENT MEDICATIONS
{current_meds_json}

# INSTRUCTIONS
- Compare medications using normalized drug names (generic names)
- Consider medications "matched" if the drug name is the same, even with dose/frequency changes
- Flag dose or frequency changes as DISCREPANCIES
- Identify medications explicitly marked as discontinued or negated
- Flag uncertain medications or unclear situations as AMBIGUITIES
- Be clinically conservative: when in doubt, flag for human review

# OUTPUT FORMAT
Provide your analysis in the following JSON structure:

```json
{{
  "matched": [
    {{
      "drug_name": "metformin",
      "prior_med_id": "uuid-123",
      "current_med_id": "uuid-456",
      "status": "continuing",
      "notes": "Same medication, same dose"
    }}
  ],
  "discrepancies": [
    {{
      "drug_name": "lisinopril",
      "prior_med_id": "uuid-789",
      "current_med_id": "uuid-012",
      "discrepancy_type": "dose_change",
      "prior_value": "10mg daily",
      "current_value": "20mg daily",
      "notes": "Dose increased from 10mg to 20mg"
    }}
  ],
  "additions": [
    {{
      "drug_name": "insulin glargine",
      "current_med_id": "uuid-345",
      "notes": "New medication added"
    }}
  ],
  "discontinuations": [
    {{
      "drug_name": "aspirin",
      "prior_med_id": "uuid-678",
      "reason": "explicitly_discontinued",
      "notes": "Patient stopped taking aspirin"
    }}
  ],
  "ambiguities": [
    {{
      "drug_name": "warfarin",
      "issue": "uncertain_status",
      "notes": "Text says 'might continue warfarin' - unclear if actually prescribed",
      "requires_review": true
    }}
  ],
  "summary": {{
    "total_prior_meds": 5,
    "total_current_meds": 6,
    "matched_count": 3,
    "discrepancy_count": 1,
    "addition_count": 2,
    "discontinuation_count": 1,
    "ambiguity_count": 1,
    "clinical_notes": "Overall stable medication regimen with one dose adjustment and two new medications."
  }}
}}
```

Now perform the reconciliation:"""
    
    def reconcile(
        self,
        prior_meds: List[MedicationEvent],
        current_meds: List[MedicationEvent]
    ) -> Dict:
        """
        Perform medication reconciliation using LLM.
        
        Args:
            prior_meds: List of medications from prior list
            current_meds: List of medications from current list
        
        Returns:
            Reconciliation results as structured dictionary
        """
        logger.info(f"Starting reconciliation: {len(prior_meds)} prior, {len(current_meds)} current")
        
        # Normalize medications
        prior_meds_normalized = self.normalizer.normalize_medication_list(prior_meds)
        current_meds_normalized = self.normalizer.normalize_medication_list(current_meds)
        
        # Convert to JSON for LLM
        prior_json = self._meds_to_json(prior_meds_normalized)
        current_json = self._meds_to_json(current_meds_normalized)
        
        # Build prompt
        prompt = self.prompt_template.format(
            prior_meds_json=prior_json,
            current_meds_json=current_json
        )
        
        # Call LLM
        logger.info("Calling LLM for reconciliation analysis")
        llm_response = self.model_engine.generate(prompt)
        
        # Parse LLM response
        reconciliation_result = self._parse_llm_response(llm_response)
        
        # Post-process and validate
        reconciliation_result = self._post_process_results(
            reconciliation_result,
            prior_meds_normalized,
            current_meds_normalized
        )
        
        logger.info("Reconciliation complete")
        return reconciliation_result
    
    def _meds_to_json(self, meds: List[MedicationEvent]) -> str:
        """
        Convert medication list to JSON string for LLM.
        
        Args:
            meds: List of MedicationEvent objects
        
        Returns:
            JSON string
        """
        meds_dict = []
        
        for med in meds:
            med_dict = {
                "med_id": med.med_id,
                "drug_name": med.drug_name_norm,
                "drug_name_raw": med.drug_name_raw,
                "dose": f"{med.dose_strength}{med.dose_unit}" if med.dose_strength and med.dose_unit else None,
                "frequency": med.frequency,
                "route": med.route,
                "form": med.form,
                "is_negated": med.is_negated,
                "is_historical": med.is_historical,
                "is_uncertain": med.is_uncertain,
                "text_snippet": med.raw_text_snippet
            }
            meds_dict.append(med_dict)
        
        return json.dumps(meds_dict, indent=2)
    
    def _parse_llm_response(self, response: str) -> Dict:
        """
        Parse LLM response into structured reconciliation result.
        
        Args:
            response: Raw LLM response
        
        Returns:
            Parsed reconciliation dictionary
        """
        try:
            # Extract JSON from response (may be wrapped in markdown)
            json_str = self._extract_json_from_response(response)
            
            # Parse JSON
            result = json.loads(json_str)
            
            return result
        
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            
            # Return empty structure on parse error
            return {
                "matched": [],
                "discrepancies": [],
                "additions": [],
                "discontinuations": [],
                "ambiguities": [],
                "summary": {
                    "error": "Failed to parse LLM response",
                    "raw_response": response[:500]
                }
            }
    
    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON content from LLM response (may be in markdown code block)."""
        import re
        
        # Try to extract from markdown code block
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, response, re.DOTALL)
        
        if match:
            return match.group(1)
        
        # Otherwise, try to find JSON object directly
        # Find first { and last }
        start_idx = response.find('{')
        end_idx = response.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            return response[start_idx:end_idx+1]
        
        raise ValueError("No JSON found in response")
    
    def _post_process_results(
        self,
        result: Dict,
        prior_meds: List[MedicationEvent],
        current_meds: List[MedicationEvent]
    ) -> Dict:
        """
        Post-process and validate reconciliation results.
        
        Args:
            result: Parsed LLM result
            prior_meds: Prior medication list
            current_meds: Current medication list
        
        Returns:
            Validated and enhanced result
        """
        # Add metadata
        result['metadata'] = {
            'prior_med_count': len(prior_meds),
            'current_med_count': len(current_meds),
            'reconciliation_method': 'llm_powered',
            'model': self.model_engine.model
        }
        
        # Validate counts match
        if 'summary' not in result:
            result['summary'] = {}
        
        result['summary']['total_prior_meds'] = len(prior_meds)
        result['summary']['total_current_meds'] = len(current_meds)
        result['summary']['matched_count'] = len(result.get('matched', []))
        result['summary']['discrepancy_count'] = len(result.get('discrepancies', []))
        result['summary']['addition_count'] = len(result.get('additions', []))
        result['summary']['discontinuation_count'] = len(result.get('discontinuations', []))
        result['summary']['ambiguity_count'] = len(result.get('ambiguities', []))
        
        return result
    
    def reconcile_medication_list(self, med_list: MedicationList) -> Dict:
        """
        Reconcile a MedicationList object.
        
        Args:
            med_list: MedicationList containing both prior and current meds
        
        Returns:
            Reconciliation results
        """
        prior_meds = med_list.get_prior_meds()
        current_meds = med_list.get_current_meds()
        
        return self.reconcile(prior_meds, current_meds)


# Example usage
if __name__ == "__main__":
    # Test the reconciliation engine
    engine = ReconciliationEngine()
    
    # Create test medication events
    prior_meds = [
        MedicationEvent(
            list_source="prior",
            drug_name_norm="metformin",
            drug_name_raw="Metformin",
            dose_strength=500.0,
            dose_unit="mg",
            frequency="BID",
            route="PO",
            raw_text_snippet="Metformin 500mg PO BID"
        ),
        MedicationEvent(
            list_source="prior",
            drug_name_norm="lisinopril",
            drug_name_raw="Lisinopril",
            dose_strength=10.0,
            dose_unit="mg",
            frequency="daily",
            route="PO",
            raw_text_snippet="Lisinopril 10mg PO daily"
        )
    ]
    
    current_meds = [
        MedicationEvent(
            list_source="current",
            drug_name_norm="metformin",
            drug_name_raw="metformin",
            dose_strength=500.0,
            dose_unit="mg",
            frequency="BID",
            route="PO",
            raw_text_snippet="Continue metformin 500mg BID"
        ),
        MedicationEvent(
            list_source="current",
            drug_name_norm="lisinopril",
            drug_name_raw="lisinopril",
            dose_strength=20.0,
            dose_unit="mg",
            frequency="daily",
            route="PO",
            raw_text_snippet="Increased lisinopril to 20mg daily"
        )
    ]
    
    # Perform reconciliation
    result = engine.reconcile(prior_meds, current_meds)
    
    print("\n=== RECONCILIATION RESULT ===")
    print(json.dumps(result, indent=2))
