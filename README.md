# VAMedRec - VA Medication Reconciliation System

A hybrid medication reconciliation application combining AI-powered reasoning with deterministic validation methods.

---

## ⚠️ **IMPORTANT DISCLAIMER**

**🚨 THIS IS A DEVELOPMENT PROTOTYPE - NOT FOR PRODUCTION USE 🚨**

**THIS SOFTWARE IS FOR RESEARCH, DEVELOPMENT, AND EDUCATIONAL PURPOSES ONLY.**

**DO NOT USE THIS APPLICATION FOR:**
- ❌ Real-time clinical decision making
- ❌ Production healthcare environments
- ❌ Patient care without clinician review
- ❌ Any situation where medication errors could cause harm
- ❌ Replacement of licensed healthcare professionals' judgment

**CRITICAL WARNINGS:**
- This is **EXPERIMENTAL SOFTWARE** under active development
- AI/LLM outputs may contain errors, hallucinations, or incomplete information
- No clinical validation or regulatory approval has been obtained
- Not compliant with HIPAA, FDA, or other healthcare regulations
- No warranty or guarantee of accuracy is provided
- **ALL outputs must be reviewed by qualified healthcare professionals**

**BY USING THIS SOFTWARE, YOU ACKNOWLEDGE:**
- You understand this is a proof-of-concept demonstration
- You will not use it for real patient care without appropriate oversight
- You accept full responsibility for any consequences of its use
- The developers assume no liability for clinical outcomes

---

## 🎯 Purpose

Automates medication reconciliation by:
- Normalizing medication data from multiple sources
- Applying deterministic safety checks
- Using LLMs for nuanced clinical reasoning
- Enforcing complete audit trails
- Preventing hallucinations and silent omissions

## 🏗️ Architecture

```
vamedrec/
├── core/                    # Core reconciliation engine
│   ├── __init__.py
│   ├── model_engine.py      # LLM interface and prompt management
│   ├── normalizer.py        # Medication normalization logic
│   └── reconciler.py        # Main reconciliation orchestrator
├── tools/                   # Utility modules
│   ├── formulary.py         # VA National Formulary interface
│   ├── safety_checks.py     # Duplication, interaction, renal/hepatic checks
│   └── ledger.py            # Audit ledger management
├── prompts/                 # LLM prompt templates
│   ├── simple_prompt.txt    # Daily reconciliation prompt
│   └── comprehensive_prompt.txt  # Admission/discharge prompt
├── examples/                # Example test cases
│   └── example_request.json
├── tests/                   # Test files
│   └── test_basic.py
├── config.py                # Centralized configuration
├── main.py                  # Web API entry point (Flask)
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
└── DEVLOG.md               # Development changelog
```

## 🔑 Key Features

### Deterministic Methods (Hardcoded)
- **Normalization**: Standardize drug names, forms, strengths, routes, frequencies
- **Directionality Tagging**: Explicit baseline vs reference list identification
- **Temporal Logic**: Handle recently expired medications (90-day rule)
- **Equivalence Detection**: Dose splitting logic ("½ 10mg" = "5mg")
- **Safety Checks**: Duplicate detection, therapeutic class conflicts, renal/hepatic contraindications
- **Ledger Enforcement**: Every input medication must appear in output with status

### AI-Powered Methods (LLM)
- **Clinical Reasoning**: Nuanced interpretation of complex cases
- **Natural Language Output**: Human-readable summaries and narratives
- **Ambiguity Handling**: Explicitly flags uncertain matches
- **Multi-step Intake**: Demographics, allergies, labs integration
- **Hallucination Prevention**: Forced "NONE" responses when appropriate

## 🚀 Quick Start

> **💡 Recommended Setup**: This project was developed in **VS Code on a VA workstation** using **GitHub Copilot**. If you have access to VS Code with GitHub Copilot, it will provide the easiest deployment experience with intelligent code assistance and automated environment setup.

### Prerequisites
- Python 3.10+ (tested with Python 3.10.11)
- VS Code (recommended) with GitHub Copilot extension
- OpenAI API key or Azure OpenAI endpoint (for production use)
- For testing: SKIP_LLM mode available (no API key required)

### Installation

**Option 1: VS Code with GitHub Copilot (Recommended)**
1. Clone the repository in VS Code
2. Open the project folder
3. Let GitHub Copilot assist with virtual environment setup
4. Use Copilot Chat to guide you through configuration

**Option 2: Manual Setup**

```powershell
# Navigate to project directory
cd "C:\Users\VHAWRJDRESCF\OneDrive - Department of Veterans Affairs\Documents\GitHub\med-reconciliation"

# Create virtual environment (Python 3.10 recommended)
py -3.10 -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Download spaCy language model (required for NLP extraction)
python -m spacy download en_core_web_sm

# Create .env file from template (optional - only needed for LLM mode)
Copy-Item .env.example .env

# Edit .env and add your API credentials (skip if using SKIP_LLM mode)
notepad .env
```

### Configuration

**For Testing (SKIP_LLM Mode - No API Key Required):**
```powershell
# Set environment variable to skip LLM calls
$env:MEDREC_SKIP_LLM='True'

# Run tests
python test_simple.py
python test_pipeline.py
```

**For Production (LLM Mode):**

Edit `.env` file and add your API credentials:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
# OR for Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-key-here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
```

### Run the Application

```powershell
# Make sure virtual environment is activated

# Option 1: Test mode (no API key needed)
$env:MEDREC_SKIP_LLM='True'
python main.py

# Option 2: Production mode (requires API key)
python main.py

# Server runs on http://localhost:5000
```

### VS Code Tips

If using **VS Code with GitHub Copilot**:
- Ask Copilot: *"How do I set up the virtual environment for this project?"*
- Ask Copilot: *"How do I configure the environment variables?"*
- Ask Copilot: *"Show me how to run the tests"*
- Use Copilot Chat to troubleshoot any dependency issues
- Copilot can help explain the codebase and suggest improvements

### Test the API

Open browser to: `http://localhost:5000`

Or test with PowerShell:
```powershell
# Simple test
$body = @{
    mode = "simple"
    baseline_meds = @(
        "Aspirin 81mg tablet by mouth daily",
        "Metformin 500mg tablet by mouth twice daily"
    )
    reference_meds = @(
        "Aspirin 81mg daily",
        "Metformin 1000mg daily"
    )
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:5000/reconcile -Method Post -Body $body -ContentType "application/json"
```

## 📊 Output Format

All reconciliations return:
1. **Structured Tables**: Markdown-compatible, EHR copy-paste ready
2. **Ledger**: Every input medication with reconciliation status
3. **Issues**: Flagged duplications, interactions, contraindications
4. **Summary**: Human-readable narrative

## 🔒 Safety Features

- **No Silent Drops**: Ledger count validation
- **No Hallucinations**: Explicit "NONE" enforcement
- **No Guessing**: Ambiguous matches flagged for human review
- **Full Traceability**: Complete audit trail

## 🛠️ Configuration

Edit `config.py` to customize:
- LLM model and endpoint
- Temperature and token limits
- Safety check thresholds
- Formulary data source
- Normalization rules

## 📖 Terminology

- **LLM**: Large Language Model (AI system for text generation)
- **Reconciliation**: Process of comparing medication lists to identify changes
- **Normalization**: Standardizing medication names/forms to common format
- **Ledger**: Audit trail showing status of every input medication
- **Directionality**: Which list is baseline ("now") vs reference ("then")
- **RAG**: Retrieval-Augmented Generation (AI + database lookup)

## 🧪 Development

See `DEVLOG.md` for detailed changelog and architectural decisions.

## 📁 Project Structure

- **`core/`**: Core business logic (normalizer, reconciler, LLM engine)
- **`tools/`**: Utility modules (safety checks, ledger, formulary)
- **`prompts/`**: LLM prompt templates
- **`examples/`**: Sample API requests and test cases
- **`tests/`**: Unit and integration tests
- **`config.py`**: Central configuration file
- **`main.py`**: Flask web API entry point

## 🤝 Contributing

This is a VA project. Follow VA security and privacy guidelines.

## 📄 License

VA Internal Use
