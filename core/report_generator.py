"""
Report Generator
Generates human-readable reconciliation reports in markdown format.
"""

from typing import Dict, List
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates actionable reconciliation reports.
    
    Outputs:
    - Markdown-formatted reports for clinical review
    - Summary statistics
    - Highlighted discrepancies and ambiguities
    - Action items for pharmacist review
    """
    
    def __init__(self):
        logger.info("Initializing ReportGenerator")
    
    def generate_report(self, reconciliation_result: Dict) -> str:
        """
        Generate markdown report from reconciliation results.
        
        Args:
            reconciliation_result: Output from ReconciliationEngine
        
        Returns:
            Markdown-formatted report string
        """
        logger.info("Generating reconciliation report")
        
        report_sections = []
        
        # Header
        report_sections.append(self._generate_header(reconciliation_result))
        
        # Executive Summary
        report_sections.append(self._generate_summary(reconciliation_result))
        
        # Matched Medications
        report_sections.append(self._generate_matched_section(reconciliation_result))
        
        # Discrepancies (Priority: HIGH)
        report_sections.append(self._generate_discrepancies_section(reconciliation_result))
        
        # Additions
        report_sections.append(self._generate_additions_section(reconciliation_result))
        
        # Discontinuations
        report_sections.append(self._generate_discontinuations_section(reconciliation_result))
        
        # Ambiguities (Priority: HIGH)
        report_sections.append(self._generate_ambiguities_section(reconciliation_result))
        
        # Action Items
        report_sections.append(self._generate_action_items(reconciliation_result))
        
        # Footer
        report_sections.append(self._generate_footer(reconciliation_result))
        
        # Combine all sections
        report = "\n\n".join(report_sections)
        
        logger.info("Report generated successfully")
        return report
    
    def _generate_header(self, result: Dict) -> str:
        """Generate report header."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""# 🏥 VAMedRec - Medication Reconciliation Report

**Generated:** {timestamp}  
**System:** VAMedRec v1.0 - VA Medication Reconciliation System
"""
    
    def _generate_summary(self, result: Dict) -> str:
        """Generate executive summary."""
        summary = result.get('summary', {})
        
        total_prior = summary.get('total_prior_meds', 0)
        total_current = summary.get('total_current_meds', 0)
        matched = summary.get('matched_count', 0)
        discrepancies = summary.get('discrepancy_count', 0)
        additions = summary.get('addition_count', 0)
        discontinuations = summary.get('discontinuation_count', 0)
        ambiguities = summary.get('ambiguity_count', 0)
        
        clinical_notes = summary.get('clinical_notes', 'No additional clinical notes.')
        
        # Calculate attention score (higher = more review needed)
        attention_score = (discrepancies * 3) + (ambiguities * 5) + (discontinuations * 2)
        
        if attention_score > 10:
            attention_level = "🔴 HIGH - Immediate pharmacist review required"
        elif attention_score > 5:
            attention_level = "🟡 MEDIUM - Review recommended"
        else:
            attention_level = "🟢 LOW - Routine review"
        
        return f"""## 📊 Executive Summary

| Metric | Count |
|--------|-------|
| **Prior Medications** | {total_prior} |
| **Current Medications** | {total_current} |
| ✅ **Matched (Continuing)** | {matched} |
| ⚠️ **Discrepancies** | {discrepancies} |
| ➕ **Additions** | {additions} |
| ❌ **Discontinuations** | {discontinuations} |
| ❓ **Ambiguities** | {ambiguities} |

**Attention Level:** {attention_level}

**Clinical Notes:** {clinical_notes}
"""
    
    def _generate_matched_section(self, result: Dict) -> str:
        """Generate matched medications section."""
        matched = result.get('matched', [])
        
        if not matched:
            return "## ✅ Matched Medications\n\n*No medications matched between lists.*"
        
        section = "## ✅ Matched Medications\n\n"
        section += f"*{len(matched)} medications continuing without significant changes.*\n\n"
        
        for med in matched:
            drug_name = med.get('drug_name', 'Unknown')
            status = med.get('status', 'continuing')
            notes = med.get('notes', '')
            
            section += f"- **{drug_name.title()}**\n"
            section += f"  - Status: {status}\n"
            if notes:
                section += f"  - Notes: {notes}\n"
        
        return section
    
    def _generate_discrepancies_section(self, result: Dict) -> str:
        """Generate discrepancies section."""
        discrepancies = result.get('discrepancies', [])
        
        if not discrepancies:
            return "## ⚠️ Discrepancies\n\n*No discrepancies identified.*"
        
        section = "## ⚠️ Discrepancies\n\n"
        section += f"**⚠️ ATTENTION REQUIRED: {len(discrepancies)} medication discrepancies detected.**\n\n"
        
        for idx, discrep in enumerate(discrepancies, 1):
            drug_name = discrep.get('drug_name', 'Unknown')
            discrep_type = discrep.get('discrepancy_type', 'unknown')
            prior_value = discrep.get('prior_value', 'N/A')
            current_value = discrep.get('current_value', 'N/A')
            notes = discrep.get('notes', '')
            
            section += f"### {idx}. {drug_name.title()}\n\n"
            section += f"- **Discrepancy Type:** {discrep_type.replace('_', ' ').title()}\n"
            section += f"- **Prior:** {prior_value}\n"
            section += f"- **Current:** {current_value}\n"
            
            if notes:
                section += f"- **Notes:** {notes}\n"
            
            section += f"- **Action Required:** Verify change with prescriber and document rationale\n\n"
        
        return section
    
    def _generate_additions_section(self, result: Dict) -> str:
        """Generate additions section."""
        additions = result.get('additions', [])
        
        if not additions:
            return "## ➕ New Medications\n\n*No new medications added.*"
        
        section = "## ➕ New Medications\n\n"
        section += f"*{len(additions)} new medications added to current regimen.*\n\n"
        
        for med in additions:
            drug_name = med.get('drug_name', 'Unknown')
            notes = med.get('notes', '')
            
            section += f"- **{drug_name.title()}**\n"
            if notes:
                section += f"  - Notes: {notes}\n"
        
        return section
    
    def _generate_discontinuations_section(self, result: Dict) -> str:
        """Generate discontinuations section."""
        discontinuations = result.get('discontinuations', [])
        
        if not discontinuations:
            return "## ❌ Discontinued Medications\n\n*No medications discontinued.*"
        
        section = "## ❌ Discontinued Medications\n\n"
        section += f"*{len(discontinuations)} medications discontinued or removed.*\n\n"
        
        for med in discontinuations:
            drug_name = med.get('drug_name', 'Unknown')
            reason = med.get('reason', 'unknown')
            notes = med.get('notes', '')
            
            section += f"- **{drug_name.title()}**\n"
            section += f"  - Reason: {reason.replace('_', ' ').title()}\n"
            if notes:
                section += f"  - Notes: {notes}\n"
        
        return section
    
    def _generate_ambiguities_section(self, result: Dict) -> str:
        """Generate ambiguities section."""
        ambiguities = result.get('ambiguities', [])
        
        if not ambiguities:
            return "## ❓ Ambiguities\n\n*No ambiguities identified.*"
        
        section = "## ❓ Ambiguities\n\n"
        section += f"**🔴 CRITICAL: {len(ambiguities)} situations require human pharmacist review.**\n\n"
        
        for idx, amb in enumerate(ambiguities, 1):
            drug_name = amb.get('drug_name', 'Unknown')
            issue = amb.get('issue', 'unknown')
            notes = amb.get('notes', '')
            requires_review = amb.get('requires_review', True)
            
            section += f"### {idx}. {drug_name.title()}\n\n"
            section += f"- **Issue:** {issue.replace('_', ' ').title()}\n"
            
            if notes:
                section += f"- **Details:** {notes}\n"
            
            if requires_review:
                section += f"- **Action Required:** Manual pharmacist review and clarification with provider\n"
            
            section += "\n"
        
        return section
    
    def _generate_action_items(self, result: Dict) -> str:
        """Generate action items for pharmacist."""
        section = "## 📋 Action Items for Pharmacist\n\n"
        
        discrepancies = result.get('discrepancies', [])
        ambiguities = result.get('ambiguities', [])
        discontinuations = result.get('discontinuations', [])
        
        action_count = 0
        
        # High priority: Ambiguities
        if ambiguities:
            action_count += 1
            section += f"{action_count}. **[HIGH PRIORITY]** Review {len(ambiguities)} ambiguous medication(s) - clarify with prescriber\n"
        
        # Medium priority: Discrepancies
        if discrepancies:
            action_count += 1
            section += f"{action_count}. **[MEDIUM PRIORITY]** Verify {len(discrepancies)} medication discrepancy(ies) - document rationale\n"
        
        # Standard: Discontinuations
        if discontinuations:
            action_count += 1
            section += f"{action_count}. **[STANDARD]** Confirm {len(discontinuations)} discontinuation(s) - update patient record\n"
        
        # Always required
        action_count += 1
        section += f"{action_count}. **[REQUIRED]** Review complete reconciliation report with patient\n"
        
        action_count += 1
        section += f"{action_count}. **[REQUIRED]** Obtain patient/provider signature on reconciliation form\n"
        
        action_count += 1
        section += f"{action_count}. **[REQUIRED]** Update electronic health record with reconciled medication list\n"
        
        if action_count == 3:
            section += "\n*No high-priority issues identified. Proceed with standard reconciliation workflow.*\n"
        
        return section
    
    def _generate_footer(self, result: Dict) -> str:
        """Generate report footer."""
        metadata = result.get('metadata', {})
        method = metadata.get('reconciliation_method', 'unknown')
        model = metadata.get('model', 'unknown')
        
        return f"""---

## ℹ️ Report Information

**Reconciliation Method:** {method}  
**AI Model:** {model}  
**System:** VAMedRec - Department of Veterans Affairs

**Disclaimer:** This report is generated using AI-assisted clinical decision support. All findings must be reviewed and validated by a licensed pharmacist or healthcare provider before clinical implementation. This system is designed to augment, not replace, professional clinical judgment.

**Questions or Issues?** Contact VA Pharmacy Services or VAMedRec Support Team.
"""
    
    def generate_json_report(self, reconciliation_result: Dict) -> str:
        """
        Generate JSON report (for API responses).
        
        Args:
            reconciliation_result: Output from ReconciliationEngine
        
        Returns:
            JSON string
        """
        import json
        return json.dumps(reconciliation_result, indent=2)


# Example usage
if __name__ == "__main__":
    # Test report generation
    generator = ReportGenerator()
    
    test_result = {
        "matched": [
            {
                "drug_name": "metformin",
                "prior_med_id": "uuid-123",
                "current_med_id": "uuid-456",
                "status": "continuing",
                "notes": "Same dose and frequency"
            }
        ],
        "discrepancies": [
            {
                "drug_name": "lisinopril",
                "prior_med_id": "uuid-789",
                "current_med_id": "uuid-012",
                "discrepancy_type": "dose_change",
                "prior_value": "10mg daily",
                "current_value": "20mg daily",
                "notes": "Dose increased for better blood pressure control"
            }
        ],
        "additions": [
            {
                "drug_name": "insulin glargine",
                "current_med_id": "uuid-345",
                "notes": "New medication for diabetes management"
            }
        ],
        "discontinuations": [
            {
                "drug_name": "aspirin",
                "prior_med_id": "uuid-678",
                "reason": "explicitly_discontinued",
                "notes": "Patient developed GI side effects"
            }
        ],
        "ambiguities": [
            {
                "drug_name": "warfarin",
                "issue": "uncertain_status",
                "notes": "Note says 'considering warfarin' but unclear if prescribed",
                "requires_review": True
            }
        ],
        "summary": {
            "total_prior_meds": 4,
            "total_current_meds": 4,
            "matched_count": 1,
            "discrepancy_count": 1,
            "addition_count": 1,
            "discontinuation_count": 1,
            "ambiguity_count": 1,
            "clinical_notes": "Patient regimen shows one dose adjustment and new diabetes medication."
        },
        "metadata": {
            "reconciliation_method": "llm_powered",
            "model": "gpt-4o"
        }
    }
    
    report = generator.generate_report(test_result)
    print(report)
