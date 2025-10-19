"""
Safety Checks Module
Implements deterministic validation: duplications, interactions, renal/hepatic checks.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from core.normalizer import Medication
import config


@dataclass
class SafetyIssue:
    """Represents a safety concern identified during validation."""
    severity: str  # "high", "moderate", "low"
    category: str  # "duplication", "interaction", "renal", "hepatic"
    description: str
    affected_meds: List[str]


class SafetyValidator:
    """Performs deterministic safety checks on medication lists."""
    
    def __init__(self):
        self.therapeutic_classes = config.THERAPEUTIC_CLASSES
        self.renal_contraindications = config.RENAL_CONTRAINDICATIONS
        self.interactions = config.HIGH_SEVERITY_INTERACTIONS
    
    def validate_all(
        self,
        medications: List[Medication],
        labs: Optional[Dict] = None
    ) -> List[SafetyIssue]:
        """
        Run all safety checks and return list of issues.
        
        Args:
            medications: List of normalized medications
            labs: Optional lab values (e.g., {"egfr": 25})
        
        Returns:
            List of SafetyIssue objects
        """
        issues = []
        
        # Check for therapeutic duplications
        issues.extend(self.check_duplications(medications))
        
        # Check for high-severity interactions
        issues.extend(self.check_interactions(medications))
        
        # Check renal/hepatic contraindications if labs provided
        if labs:
            issues.extend(self.check_renal_contraindications(medications, labs))
        
        return issues
    
    def check_duplications(self, medications: List[Medication]) -> List[SafetyIssue]:
        """
        Check for therapeutic duplications (same class, different drugs).
        Also checks for exact duplicate (same drug multiple times).
        """
        issues = []
        
        # Exact duplicates (same generic name)
        seen_generics = {}
        for med in medications:
            generic = med.generic_name
            if generic in seen_generics:
                issues.append(SafetyIssue(
                    severity="moderate",
                    category="duplication",
                    description=f"Duplicate medication: {generic} appears multiple times",
                    affected_meds=[generic]
                ))
            seen_generics[generic] = True
        
        # Therapeutic class duplications
        for class_name, drug_list in self.therapeutic_classes.items():
            found_drugs = [
                med.generic_name for med in medications
                if med.generic_name in drug_list
            ]
            
            if len(found_drugs) > 1:
                issues.append(SafetyIssue(
                    severity="moderate",
                    category="duplication",
                    description=f"Multiple {class_name} drugs: {', '.join(found_drugs)}",
                    affected_meds=found_drugs
                ))
        
        return issues
    
    def check_interactions(self, medications: List[Medication]) -> List[SafetyIssue]:
        """Check for high-severity drug interactions."""
        issues = []
        med_names = [med.generic_name for med in medications]
        
        for interaction in self.interactions:
            drug1 = interaction["drug1"]
            drug2 = interaction["drug2"]
            
            # Check if both drugs present
            drug1_present = any(drug1 in name for name in med_names)
            drug2_present = any(drug2 in name for name in med_names)
            
            if drug1_present and drug2_present:
                issues.append(SafetyIssue(
                    severity="high",
                    category="interaction",
                    description=f"{drug1.title()} + {drug2.title()}: {interaction['risk']}",
                    affected_meds=[drug1, drug2]
                ))
        
        return issues
    
    def check_renal_contraindications(
        self,
        medications: List[Medication],
        labs: Dict
    ) -> List[SafetyIssue]:
        """
        Check medications against renal function.
        
        Args:
            medications: List of medications
            labs: Dictionary with "egfr" key (mL/min/1.73m²)
        """
        issues = []
        egfr = labs.get("egfr")
        
        if egfr is None:
            return issues
        
        for med in medications:
            generic = med.generic_name
            
            # Check exact matches
            if generic in self.renal_contraindications:
                contraindication = self.renal_contraindications[generic]
                if egfr < contraindication["egfr_threshold"]:
                    issues.append(SafetyIssue(
                        severity="high",
                        category="renal",
                        description=(
                            f"{generic.title()} contraindicated with eGFR {egfr} "
                            f"(threshold: {contraindication['egfr_threshold']}). "
                            f"Reason: {contraindication['reason']}"
                        ),
                        affected_meds=[generic]
                    ))
            
            # Check class-based contraindications (e.g., "nsaid")
            for contraindicated_class, contraindication in self.renal_contraindications.items():
                if contraindicated_class in self.therapeutic_classes:
                    class_drugs = self.therapeutic_classes[contraindicated_class]
                    if generic in class_drugs and egfr < contraindication["egfr_threshold"]:
                        issues.append(SafetyIssue(
                            severity="high",
                            category="renal",
                            description=(
                                f"{generic.title()} ({contraindicated_class.upper()}) "
                                f"contraindicated with eGFR {egfr}. "
                                f"Reason: {contraindication['reason']}"
                            ),
                            affected_meds=[generic]
                        ))
        
        return issues
    
    def format_issues_table(self, issues: List[SafetyIssue]) -> str:
        """Format safety issues as markdown table."""
        if not issues:
            return "**No safety issues detected.**"
        
        table = "| Severity | Category | Description | Medications |\n"
        table += "|----------|----------|-------------|-------------|\n"
        
        for issue in issues:
            severity_emoji = {
                "high": "🔴",
                "moderate": "🟡",
                "low": "🟢"
            }.get(issue.severity, "")
            
            table += (
                f"| {severity_emoji} {issue.severity.title()} "
                f"| {issue.category.title()} "
                f"| {issue.description} "
                f"| {', '.join(issue.affected_meds)} |\n"
            )
        
        return table
