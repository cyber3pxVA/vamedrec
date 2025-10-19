"""
Main Reconciliation Orchestrator
Coordinates normalization, LLM reasoning, validation, and ledger management.
"""

from typing import Dict, List, Optional
from core.normalizer import MedicationNormalizer, Medication
from core.model_engine import ModelEngine
from tools.safety_checks import SafetyValidator
from tools.ledger import ReconciliationLedger


class MedicationReconciler:
    """
    Main orchestrator for medication reconciliation process.
    Combines deterministic preprocessing with LLM-powered reasoning.
    """
    
    def __init__(self):
        self.normalizer = MedicationNormalizer()
        self.model_engine = ModelEngine()
        self.safety_validator = SafetyValidator()
    
    def reconcile(
        self,
        baseline_meds: List[str],
        reference_meds: List[str],
        mode: str = "simple",
        patient_context: Optional[Dict] = None,
        baseline_label: str = "Current (Now)",
        reference_label: str = "Previous (Then)"
    ) -> Dict:
        """
        Perform complete medication reconciliation.
        
        Args:
            baseline_meds: Current medication list (the "now")
            reference_meds: Previous medication list (the "then")
            mode: "simple" or "comprehensive"
            patient_context: Optional patient data (demographics, labs, etc.)
            baseline_label: Label for baseline list
            reference_label: Label for reference list
        
        Returns:
            Dictionary containing:
                - normalized_baseline: List of normalized medications
                - normalized_reference: List of normalized medications
                - llm_output: Raw LLM reconciliation text
                - safety_issues: List of safety concerns
                - ledger: Reconciliation ledger
                - summary: Overall summary
        """
        # Step 1: Normalize medications
        normalized_baseline = self.normalizer.normalize_batch(baseline_meds)
        normalized_reference = self.normalizer.normalize_batch(reference_meds)
        
        # Step 2: Tag directionality
        tagged = self.normalizer.tag_directionality(
            normalized_baseline,
            normalized_reference,
            baseline_label,
            reference_label
        )
        
        # Step 3: Run deterministic safety checks (on combined list)
        all_meds = normalized_baseline + normalized_reference
        labs = patient_context.get("labs") if patient_context else None
        safety_issues = self.safety_validator.validate_all(all_meds, labs)
        
        # Step 4: Call LLM for reconciliation reasoning
        if mode == "simple":
            llm_output = self.model_engine.reconcile_simple(
                baseline_meds,
                reference_meds,
                baseline_label,
                reference_label
            )
        elif mode == "comprehensive":
            llm_output = self.model_engine.reconcile_comprehensive(
                baseline_meds,
                reference_meds,
                patient_context,
                baseline_label,
                reference_label
            )
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be 'simple' or 'comprehensive'.")
        
        # Step 5: Build reconciliation ledger
        ledger = self._build_ledger(
            normalized_baseline,
            normalized_reference,
            llm_output
        )
        
        # Step 6: Validate ledger completeness
        all_input_meds = normalized_baseline + normalized_reference
        validation = ledger.validate_completeness(all_input_meds)
        
        # Step 7: Compile results
        result = {
            "normalized_baseline": [self._med_to_dict(m) for m in normalized_baseline],
            "normalized_reference": [self._med_to_dict(m) for m in normalized_reference],
            "llm_output": llm_output,
            "safety_issues": safety_issues,
            "safety_issues_table": self.safety_validator.format_issues_table(safety_issues),
            "ledger": ledger,
            "ledger_validation": validation,
            "summary": self._generate_summary(ledger, safety_issues, validation)
        }
        
        return result
    
    def _build_ledger(
        self,
        baseline_meds: List[Medication],
        reference_meds: List[Medication],
        llm_output: str
    ) -> ReconciliationLedger:
        """
        Build reconciliation ledger from normalized meds and LLM output.
        This is a simplified implementation - in production, you'd parse
        the LLM output more carefully to assign statuses.
        """
        ledger = ReconciliationLedger()
        
        # For now, we'll use a heuristic: check if meds from baseline
        # match anything in reference
        baseline_generics = {m.generic_name: m for m in baseline_meds}
        reference_generics = {m.generic_name: m for m in reference_meds}
        
        # Process baseline medications
        for med in baseline_meds:
            if med.generic_name in reference_generics:
                ref_med = reference_generics[med.generic_name]
                
                # Check if changed
                if self.normalizer.check_equivalence(med, ref_med):
                    status = "Continued—No Change"
                else:
                    status = "Changed"
            else:
                status = "New"
            
            ledger.add_entry(
                input_med=med,
                status=status,
                output_med=med.raw_input,
                notes=""
            )
        
        # Process reference medications not in baseline (stopped meds)
        for med in reference_meds:
            if med.generic_name not in baseline_generics:
                ledger.add_entry(
                    input_med=med,
                    status="Not Continued",
                    output_med="",
                    notes="Not continued from previous list"
                )
        
        return ledger
    
    def _med_to_dict(self, med: Medication) -> Dict:
        """Convert Medication object to dictionary for JSON serialization."""
        return {
            "raw_input": med.raw_input,
            "name": med.name,
            "generic_name": med.generic_name,
            "strength": med.strength,
            "form": med.form,
            "route": med.route,
            "frequency": med.frequency,
            "normalized_dose": med.normalized_dose,
        }
    
    def _generate_summary(
        self,
        ledger: ReconciliationLedger,
        safety_issues: List,
        validation: Dict
    ) -> str:
        """Generate overall summary of reconciliation."""
        summary = "# Medication Reconciliation Summary\n\n"
        
        # Ledger summary
        ledger_summary = ledger.get_summary()
        summary += "## Reconciliation Status\n\n"
        for status, count in ledger_summary.items():
            if count > 0:
                summary += f"- **{status}:** {count}\n"
        
        # Validation status
        summary += f"\n## Ledger Validation\n\n"
        if validation["is_complete"]:
            summary += "✅ **Complete** - All input medications accounted for.\n"
        else:
            summary += f"⚠️ **Incomplete** - {validation['missing_count']} medications not accounted for.\n"
        
        # Safety issues
        summary += f"\n## Safety Issues\n\n"
        if safety_issues:
            summary += f"⚠️ {len(safety_issues)} safety issue(s) identified. See detailed report below.\n"
        else:
            summary += "✅ No safety issues detected.\n"
        
        return summary
    
    def format_output(self, result: Dict) -> str:
        """
        Format complete reconciliation output as markdown.
        
        Args:
            result: Result dictionary from reconcile()
        
        Returns:
            Formatted markdown string
        """
        output = "# Medication Reconciliation Report\n\n"
        output += "---\n\n"
        
        # Summary
        output += result["summary"]
        output += "\n---\n\n"
        
        # LLM Output
        output += "## Clinical Reconciliation\n\n"
        output += result["llm_output"]
        output += "\n\n---\n\n"
        
        # Safety Issues
        output += "## Safety Issues\n\n"
        output += result["safety_issues_table"]
        output += "\n\n---\n\n"
        
        # Ledger
        output += result["ledger"].format_as_table()
        output += "\n\n---\n\n"
        
        # Issues for Review
        output += result["ledger"].format_issues_section()
        
        return output
