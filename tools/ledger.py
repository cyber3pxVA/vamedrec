"""
Audit Ledger Management
Ensures every input medication is accounted for in the output.
Prevents silent drops and enforces reconciliation completeness.
"""

from typing import List, Dict
from dataclasses import dataclass
from core.normalizer import Medication
import config


@dataclass
class LedgerEntry:
    """Single entry in the reconciliation ledger."""
    input_medication: str
    reconciliation_status: str  # New, Not Continued, Changed, Continued—No Change, Unmatched—Verify
    output_medication: str = ""
    notes: str = ""


class ReconciliationLedger:
    """Manages the audit trail for medication reconciliation."""
    
    def __init__(self):
        self.entries: List[LedgerEntry] = []
        self.valid_statuses = config.LEDGER_STATUSES
    
    def add_entry(
        self,
        input_med: Medication,
        status: str,
        output_med: str = "",
        notes: str = ""
    ) -> None:
        """
        Add an entry to the ledger.
        
        Args:
            input_med: Input medication object
            status: Reconciliation status (must be in LEDGER_STATUSES)
            output_med: Output medication string (if changed/continued)
            notes: Additional notes or explanations
        """
        if status not in self.valid_statuses:
            raise ValueError(
                f"Invalid status '{status}'. Must be one of: {self.valid_statuses}"
            )
        
        entry = LedgerEntry(
            input_medication=input_med.raw_input,
            reconciliation_status=status,
            output_medication=output_med,
            notes=notes
        )
        self.entries.append(entry)
    
    def validate_completeness(
        self,
        input_medications: List[Medication]
    ) -> Dict[str, any]:
        """
        Validate that all input medications appear in the ledger.
        
        Args:
            input_medications: Original list of input medications
        
        Returns:
            Dictionary with validation results
        """
        input_count = len(input_medications)
        ledger_count = len(self.entries)
        
        is_complete = input_count == ledger_count
        
        result = {
            "is_complete": is_complete,
            "input_count": input_count,
            "ledger_count": ledger_count,
            "missing_count": input_count - ledger_count if not is_complete else 0,
        }
        
        if not is_complete:
            # Identify missing medications
            input_raws = {med.raw_input for med in input_medications}
            ledger_raws = {entry.input_medication for entry in self.entries}
            missing = input_raws - ledger_raws
            result["missing_medications"] = list(missing)
        
        return result
    
    def get_summary(self) -> Dict[str, int]:
        """Get count summary by reconciliation status."""
        summary = {status: 0 for status in self.valid_statuses}
        
        for entry in self.entries:
            summary[entry.reconciliation_status] += 1
        
        return summary
    
    def format_as_table(self) -> str:
        """Format ledger as markdown table."""
        if not self.entries:
            return "**Ledger is empty.**"
        
        table = "## Reconciliation Ledger\n\n"
        table += "| # | Input Medication | Status | Output Medication | Notes |\n"
        table += "|---|------------------|--------|-------------------|-------|\n"
        
        for idx, entry in enumerate(self.entries, 1):
            table += (
                f"| {idx} "
                f"| {entry.input_medication} "
                f"| {entry.reconciliation_status} "
                f"| {entry.output_medication} "
                f"| {entry.notes} |\n"
            )
        
        # Add summary
        summary = self.get_summary()
        table += f"\n**Total Medications:** {len(self.entries)}\n\n"
        
        for status, count in summary.items():
            if count > 0:
                table += f"- {status}: {count}\n"
        
        return table
    
    def format_summary_section(self) -> str:
        """Format a concise summary for the output."""
        summary = self.get_summary()
        total = len(self.entries)
        
        output = "### Summary\n\n"
        output += f"**Total Medications Reconciled:** {total}\n\n"
        
        for status, count in summary.items():
            if count > 0:
                output += f"- **{status}:** {count}\n"
        
        return output
    
    def get_issues_for_review(self) -> List[LedgerEntry]:
        """Return entries that require human review."""
        return [
            entry for entry in self.entries
            if entry.reconciliation_status == "Unmatched—Verify"
        ]
    
    def format_issues_section(self) -> str:
        """Format issues requiring review."""
        issues = self.get_issues_for_review()
        
        if not issues:
            return "### Issues to Review\n\n**None** - All medications successfully matched.\n"
        
        output = "### Issues to Review\n\n"
        output += "The following medications require clinician verification:\n\n"
        
        for idx, entry in enumerate(issues, 1):
            output += f"{idx}. **{entry.input_medication}**\n"
            if entry.notes:
                output += f"   - {entry.notes}\n"
        
        return output
