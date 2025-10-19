# VAMedRec - Development Log

## 2025-01-19: Initial Project Setup

### Architecture Decisions

**Modular Structure**
- Separated core logic (`core/`) from utilities (`tools/`) and entry points (`main.py`)
- Isolated LLM interaction in `model_engine.py` for easy model swapping
- Centralized configuration in `config.py` for maintainability

**Hybrid Approach**
- Deterministic preprocessing handles normalization, equivalence, and safety checks
- LLM handles nuanced reasoning, narrative generation, and ambiguity detection
- Two-stage validation: deterministic rules first, then LLM augmentation

**Design Philosophy (Braun-Inspired)**
- Clean, minimal, purposeful
- Every component has a single responsibility
- No feature bloat—only essential medication reconciliation functionality
- Modular structure for easy testing and maintenance

### Key Technical Choices

**Python + Flask**
- Python for healthcare data processing libraries
- Flask for lightweight API (easily upgradeable to FastAPI if async needed)
- Simple REST API design for easy integration

**Ledger-First Design**
- Every medication tracked through complete reconciliation pipeline
- Count validation prevents silent omissions
- Status field enforces explicit reconciliation decision
- Full audit trail for compliance

**Prompt Engineering**
- Two separate prompts: simple (daily) and comprehensive (admission/discharge)
- Structured output format with explicit hallucination prevention
- Directionality and inclusion criteria explicitly stated in prompts
- System message emphasizes precision and evidence-based reasoning

**Safety-First Implementation**
- Deterministic checks run before LLM (fail-fast on critical issues)
- Renal/hepatic contraindication checking with lab integration
- Drug interaction database (expandable)
- Therapeutic class duplication detection

### Dependencies Rationale

- `openai==1.54.3`: LLM API access (compatible with Azure OpenAI)
- `flask==3.0.3`: Web API framework
- `python-dotenv==1.0.1`: Environment configuration management
- `pydantic==2.9.2`: Data validation and serialization
- `pandas==2.2.3`: Medication data manipulation (optional, for future enhancements)
- `requests==2.32.3`: HTTP client for potential external API calls

### File Organization

**Core Modules (`core/`)**
- `normalizer.py`: Medication string parsing and standardization
- `model_engine.py`: LLM interface with prompt management
- `reconciler.py`: Main orchestration logic

**Tools Modules (`tools/`)**
- `safety_checks.py`: Deterministic validation rules
- `ledger.py`: Audit trail management
- `formulary.py`: VA National Formulary interface (placeholder for future)

**Configuration**
- `config.py`: All settings, thresholds, and mappings
- `.env`: Sensitive credentials (git-ignored)

### Security Considerations

- API keys stored in environment variables only
- `.env` file excluded from git
- No PHI/PII in logs or examples
- All examples use synthetic data

### Next Steps

1. ✅ Implement core normalization engine
2. ✅ Build safety check validators
3. ✅ Create LLM prompt templates
4. ✅ Wire up API endpoints
5. ⏳ Add comprehensive testing
6. ⏳ Implement RAG with VA Formulary
7. ⏳ Add multi-LLM validation pipeline
8. ⏳ Performance optimization
9. ⏳ EHR integration adapters

### Testing Strategy

- Unit tests for normalization logic
- Integration tests for full reconciliation flow
- Mock LLM responses for CI/CD
- Real-world test cases from de-identified scenarios

### Future Enhancements

- **RAG Implementation**: Integrate VA National Formulary lookups
- **Multi-LLM Validation**: Use second model to validate first model's output
- **Batch Processing**: Handle multiple patients efficiently
- **EHR Integration**: Direct CPRS/JLV data pull
- **Audit Dashboard**: Web UI for reviewing reconciliations
- **ML-Based Matching**: Train local model on past reconciliations
