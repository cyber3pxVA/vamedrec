# 📋 Medication Reconciliation Pipeline - Implementation Plan

## Overview
This document outlines the implementation of a 3-stage medication reconciliation pipeline combining deterministic clinical NLP (medSpaCy) with LLM-powered analysis.

## Architecture

### Stage 1: Deterministic Extraction
- **Tool:** medSpaCy + Duckling
- **Input:** Raw clinical text (prior and current notes)
- **Output:** Structured JSON entities with context

### Stage 2: Data Normalization
- **Tool:** Custom Python normalizers
- **Input:** Raw entities from Stage 1
- **Output:** Standardized medication_events list

### Stage 3: LLM Reconciliation
- **Tool:** Azure OpenAI (GPT-4o)
- **Input:** Normalized medication_events JSON
- **Output:** Markdown reconciliation report

---

## Implementation Status

### ✅ Already Implemented (Existing VAMedRec)
- Azure OpenAI integration
- Flask API framework
- Configuration management
- Docker deployment
- CI/CD pipeline

### 🚧 To Implement (Med Rec Pipeline)
- [ ] medSpaCy clinical entity extraction
- [ ] Duckling temporal parser integration
- [ ] Context detection (negation, historical)
- [ ] RxNorm/UMLS normalization
- [ ] Medication event JSON schema
- [ ] Reconciliation logic
- [ ] Report generation

---

## File Structure

```
vamedrec/
├── core/
│   ├── clinical_extractor.py      # NEW: medSpaCy extraction
│   ├── temporal_parser.py         # NEW: Duckling integration
│   ├── med_normalizer.py          # NEW: Medication normalization
│   ├── reconciliation_engine.py   # NEW: Reconciliation logic
│   └── report_generator.py        # NEW: Final report creation
├── models/
│   └── med_event.py               # NEW: Medication event schema
├── prompts/
│   └── reconciliation_prompt.txt  # NEW: LLM reconciliation prompt
└── requirements.txt               # UPDATE: Add medSpaCy, duckling

```

---

## Next Steps

1. Install medSpaCy and dependencies
2. Implement clinical entity extractor
3. Add temporal parser
4. Create medication event schema
5. Build reconciliation engine
6. Create report generator
7. Update API endpoints
8. Add tests and examples

---

**Status:** Ready for implementation
**Priority:** HIGH
**Estimated Effort:** 2-3 days
