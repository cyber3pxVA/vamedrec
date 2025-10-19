"""
Medication Event Data Model
Defines the structured schema for medication events extracted from clinical text.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import uuid


class MedicationEvent(BaseModel):
    """
    Structured representation of a single medication mention in clinical text.
    
    This schema represents the output of Stage 1 (Deterministic Extraction)
    and Stage 2 (Normalization) of the Med Rec pipeline.
    """
    
    # Source and Identification
    list_source: Literal["prior", "current"] = Field(
        description="Which list this medication came from"
    )
    
    med_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for this medication event"
    )
    
    # Drug Information (Normalized)
    drug_name_norm: str = Field(
        description="Normalized drug name (RxNorm/UMLS concept)"
    )
    
    drug_name_raw: Optional[str] = Field(
        default=None,
        description="Original drug name as found in text"
    )
    
    rxnorm_cui: Optional[str] = Field(
        default=None,
        description="RxNorm Concept Unique Identifier"
    )
    
    # Dosing Information
    dose_strength: Optional[float] = Field(
        default=None,
        description="Numeric dose amount (e.g., 500.0)"
    )
    
    dose_unit: Optional[str] = Field(
        default=None,
        description="Unit of measure (e.g., 'mg', 'mcg', 'units')"
    )
    
    form: Optional[str] = Field(
        default=None,
        description="Drug form (e.g., 'tablet', 'capsule', 'injection')"
    )
    
    # Administration Details
    frequency: Optional[str] = Field(
        default=None,
        description="Frequency of administration (e.g., 'BID', 'QHS', 'twice daily')"
    )
    
    route: Optional[str] = Field(
        default=None,
        description="Route of administration (e.g., 'PO', 'IV', 'subcutaneous')"
    )
    
    # Clinical Context Flags
    is_negated: bool = Field(
        default=False,
        description="True if medication is explicitly denied or discontinued"
    )
    
    is_historical: bool = Field(
        default=False,
        description="True if medication is mentioned as past/historical"
    )
    
    is_family_history: bool = Field(
        default=False,
        description="True if medication is mentioned as family member's"
    )
    
    is_uncertain: bool = Field(
        default=False,
        description="True if text contains uncertainty markers (might, maybe, considering)"
    )
    
    # Temporal Information
    date_of_change_iso: Optional[str] = Field(
        default=None,
        description="ISO 8601 formatted date if temporal reference found (e.g., '2025-10-19')"
    )
    
    temporal_expression: Optional[str] = Field(
        default=None,
        description="Original temporal expression (e.g., '3 weeks ago', 'since January')"
    )
    
    # Source Text
    raw_text_snippet: str = Field(
        description="The sentence or phrase where the medication was extracted"
    )
    
    sentence_context: Optional[str] = Field(
        default=None,
        description="Broader context (e.g., full paragraph) if available"
    )
    
    # Extraction Metadata
    extraction_confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score from entity extraction (0.0 to 1.0)"
    )
    
    extraction_method: Optional[str] = Field(
        default="medspacy",
        description="Method used for extraction (e.g., 'medspacy', 'quickumls')"
    )
    
    extracted_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when this event was extracted"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "list_source": "current",
                "med_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "drug_name_norm": "Metformin",
                "drug_name_raw": "metformin",
                "rxnorm_cui": "6809",
                "dose_strength": 500.0,
                "dose_unit": "mg",
                "form": "tablet",
                "frequency": "BID",
                "route": "PO",
                "is_negated": False,
                "is_historical": False,
                "is_family_history": False,
                "is_uncertain": False,
                "date_of_change_iso": "2025-10-01",
                "temporal_expression": "started last month",
                "raw_text_snippet": "Patient started metformin 500mg PO BID last month",
                "sentence_context": "For diabetes management, patient started metformin 500mg PO BID last month.",
                "extraction_confidence": 0.95,
                "extraction_method": "medspacy",
                "extracted_at": "2025-10-19T12:00:00Z"
            }
        }


class MedicationList(BaseModel):
    """Collection of medication events for a single patient encounter."""
    
    patient_id: Optional[str] = Field(
        default=None,
        description="Patient identifier (if available)"
    )
    
    encounter_id: Optional[str] = Field(
        default=None,
        description="Encounter or visit identifier"
    )
    
    reconciliation_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Date of reconciliation"
    )
    
    medications: list[MedicationEvent] = Field(
        default_factory=list,
        description="List of all medication events"
    )
    
    prior_text_source: Optional[str] = Field(
        default=None,
        description="Source of prior medication list (e.g., 'EHR', 'Patient Interview')"
    )
    
    current_text_source: Optional[str] = Field(
        default=None,
        description="Source of current medication notes (e.g., 'Progress Note', 'Discharge Summary')"
    )
    
    def get_prior_meds(self) -> list[MedicationEvent]:
        """Return only medications from the prior list."""
        return [med for med in self.medications if med.list_source == "prior"]
    
    def get_current_meds(self) -> list[MedicationEvent]:
        """Return only medications from the current list."""
        return [med for med in self.medications if med.list_source == "current"]
    
    def get_active_meds(self) -> list[MedicationEvent]:
        """Return only active (not negated/historical) medications."""
        return [
            med for med in self.medications
            if not med.is_negated and not med.is_historical
        ]
    
    def get_discontinued_meds(self) -> list[MedicationEvent]:
        """Return only discontinued/negated medications."""
        return [med for med in self.medications if med.is_negated]
    
    def get_uncertain_meds(self) -> list[MedicationEvent]:
        """Return medications flagged as uncertain."""
        return [med for med in self.medications if med.is_uncertain]
