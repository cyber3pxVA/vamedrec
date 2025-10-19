# Clinical Med Rec Pipeline - Implementation Guide

## Overview

The VAMedRec Clinical Medication Reconciliation Pipeline is a comprehensive, three-stage system that combines deterministic NLP extraction with LLM-powered reasoning for accurate medication reconciliation.

## Architecture

### **Stage 1: Deterministic Extraction**
- **Technology**: medSpaCy + Duckling
- **Purpose**: Extract medication entities and clinical context from free text
- **Outputs**: Structured MedicationEvent objects

**Components:**
- `ClinicalExtractor`: Extracts drug names, doses, frequencies, routes
- `TemporalParser`: Extracts and normalizes temporal expressions
- **Context Detection**: Negation, historical status, family history, uncertainty

### **Stage 2: Data Normalization**
- **Technology**: RxNorm/UMLS mapping
- **Purpose**: Standardize medication names, doses, routes, frequencies
- **Outputs**: Normalized MedicationEvent objects

**Components:**
- `MedicationNormalizer`: Brand→generic mapping, dose unit standardization
- **QuickUMLS Integration** (optional): RxNorm CUI mapping

### **Stage 3: LLM-Powered Reconciliation**
- **Technology**: Azure OpenAI GPT-4o
- **Purpose**: Compare prior vs current medications and identify discrepancies
- **Outputs**: Structured reconciliation report with actionable insights

**Components:**
- `ReconciliationEngine`: LLM-powered comparison logic
- `ReportGenerator`: Markdown report generation
- **Reconciliation Categories**: Matched, Discrepancies, Additions, Discontinuations, Ambiguities

## File Structure

```
core/
├── clinical_extractor.py      # Stage 1: medSpaCy extraction
├── temporal_parser.py          # Stage 1: Temporal parsing
├── med_normalizer.py           # Stage 2: Normalization
├── reconciliation_engine.py    # Stage 3: LLM reconciliation
├── report_generator.py         # Report generation
└── med_rec_pipeline.py         # Pipeline orchestrator

models/
└── med_event.py                # Pydantic data models

prompts/
└── reconciliation_prompt.txt   # LLM prompt template
```

## Data Models

### MedicationEvent
Represents a single medication mention extracted from clinical text:

```python
{
  "list_source": "prior" | "current",
  "med_id": "uuid",
  "drug_name_norm": "metformin",
  "drug_name_raw": "Metformin",
  "rxnorm_cui": "6809",
  "dose_strength": 500.0,
  "dose_unit": "mg",
  "form": "tablet",
  "frequency": "BID",
  "route": "PO",
  "is_negated": false,
  "is_historical": false,
  "is_uncertain": false,
  "date_of_change_iso": "2025-10-19",
  "temporal_expression": "3 weeks ago",
  "raw_text_snippet": "Patient stopped aspirin 3 weeks ago",
  "extraction_confidence": 0.95,
  "extraction_method": "medspacy"
}
```

### MedicationList
Collection of medication events for reconciliation:

```python
{
  "patient_id": "VA-12345678",
  "encounter_id": "ENC-2025-10-19-001",
  "reconciliation_date": "2025-10-19T12:00:00",
  "medications": [MedicationEvent, ...],
  "prior_text_source": "Home Medication List",
  "current_text_source": "Progress Note"
}
```

## API Usage

### Endpoint: `/reconcile_clinical`

**Request:**
```json
{
  "prior_text": "PRIOR MEDICATION LIST:\n1. Metformin 500mg PO BID\n2. Lisinopril 10mg PO daily",
  "current_text": "CURRENT MEDICATIONS:\nPatient continues metformin 500mg BID.\nIncreased lisinopril to 20mg daily.",
  "patient_id": "VA-12345678",
  "encounter_id": "ENC-2025-10-19-001",
  "output_format": "markdown"
}
```

**Response (markdown format):**
```json
{
  "success": true,
  "pipeline": "clinical_nlp_3_stage",
  "report_markdown": "# Medication Reconciliation Report\n...",
  "summary": {
    "total_prior_meds": 2,
    "total_current_meds": 2,
    "matched_count": 2,
    "discrepancy_count": 1,
    "addition_count": 0,
    "discontinuation_count": 0,
    "ambiguity_count": 0
  },
  "metadata": {
    "pipeline_version": "1.0",
    "stages_completed": ["extraction", "normalization", "reconciliation"],
    "timestamp": "2025-10-19T12:00:00"
  }
}
```

**Response (json format):**
Set `"output_format": "json"` to get full structured data including all medication events and reconciliation details.

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### 3. Configure Environment

Create `.env` file:
```
AZURE_ENDPOINT=https://your-openai-endpoint.azure-api.us/api
OPENAI_API_KEY=your-api-key-here
MODEL_NAME=gpt-4o
```

### 4. Run Tests

```bash
python test_pipeline.py
```

## Usage Examples

### Python API

```python
from core.med_rec_pipeline import MedRecPipeline

# Initialize pipeline
pipeline = MedRecPipeline()

# Define clinical texts
prior_text = """
PRIOR MEDICATIONS:
1. Metformin 500mg PO BID
2. Lisinopril 10mg PO daily
"""

current_text = """
CURRENT MEDICATIONS:
- Continue metformin 500mg BID
- Increased lisinopril to 20mg daily
"""

# Run full pipeline
result = pipeline.run_full_pipeline(
    prior_text=prior_text,
    current_text=current_text,
    patient_id="VA-12345678"
)

# Print markdown report
print(result['report_markdown'])

# Access structured data
summary = result['reconciliation']['summary']
print(f"Discrepancies: {summary['discrepancy_count']}")
```

### REST API (cURL)

```bash
curl -X POST http://localhost:5000/reconcile_clinical \
  -H "Content-Type: application/json" \
  -d @examples/example_clinical_reconciliation.json
```

## Pipeline Output Categories

### 1. **Matched** ✅
Medications continuing without significant changes
- Same drug name (brand/generic equivalent)
- Same or similar dose/frequency

### 2. **Discrepancies** ⚠️
Medications with changes requiring review
- Dose changes
- Frequency changes
- Route changes
- Form changes

### 3. **Additions** ➕
New medications not in prior list

### 4. **Discontinuations** ❌
Medications removed or stopped
- Explicitly discontinued (negated)
- Implicitly missing from current list

### 5. **Ambiguities** ❓
Unclear situations requiring human review
- Uncertain status ("might start...")
- Conflicting information
- Unclear dosing

## Performance Considerations

### Extraction Performance
- **Speed**: ~100-500ms per document (depends on length)
- **Accuracy**: medSpaCy achieves ~85-90% F1 on clinical entity extraction

### LLM Performance
- **Speed**: ~2-5 seconds per reconciliation (Azure OpenAI)
- **Cost**: ~$0.01-0.03 per reconciliation (GPT-4o pricing)
- **Accuracy**: Human review recommended for all reconciliations

### Scalability
- **Batch Processing**: Process multiple reconciliations in parallel
- **Caching**: Cache normalized drug names for faster processing
- **Rate Limiting**: Implement rate limiting for LLM calls

## Safety & Compliance

### Clinical Validation
⚠️ **CRITICAL**: All reconciliations must be reviewed by a licensed pharmacist or healthcare provider before clinical implementation.

### Data Privacy
- **PHI Protection**: All patient data must be handled per HIPAA regulations
- **Audit Trails**: All reconciliations are logged with timestamps
- **Access Control**: Implement proper authentication/authorization

### Error Handling
- **Extraction Failures**: Log and flag for manual review
- **LLM Failures**: Fallback to manual reconciliation
- **Validation**: All outputs include confidence scores

## Troubleshooting

### medSpaCy Installation Issues
```bash
# Install with specific versions
pip install spacy==3.7.2
pip install medspacy==1.0.0
python -m spacy download en_core_web_sm
```

### QuickUMLS (Optional)
QuickUMLS requires UMLS data download. If not available, the pipeline will work without RxNorm CUI mapping.

### Azure OpenAI Connection
Verify your `.env` configuration:
- `AZURE_ENDPOINT` must be your Azure OpenAI endpoint URL
- `OPENAI_API_KEY` must be your API key
- `MODEL_NAME` must match your deployment name (e.g., `gpt-4o`)

## Development

### Adding Custom Medication Patterns
Edit `core/clinical_extractor.py`:
```python
def _add_medication_patterns(self):
    patterns = [
        # Add your custom patterns here
    ]
```

### Customizing Reconciliation Logic
Edit `prompts/reconciliation_prompt.txt` to modify LLM behavior.

### Testing
```bash
# Run full test suite
python test_pipeline.py

# Test individual components
python core/clinical_extractor.py
python core/med_normalizer.py
python core/reconciliation_engine.py
```

## Future Enhancements

- [ ] Enhanced RxNorm/UMLS integration
- [ ] Drug interaction detection
- [ ] Allergy checking
- [ ] Dose range validation
- [ ] Multi-language support
- [ ] Real-time EHR integration
- [ ] Mobile app interface

## Support

For questions or issues:
- GitHub: https://github.com/cyber3pxVA/vamedrec
- Documentation: See `MED_REC_PIPELINE.md`
- VA Support: Contact VA Pharmacy Services

## License

This project is intended for use within the Department of Veterans Affairs. Unauthorized distribution is prohibited.
