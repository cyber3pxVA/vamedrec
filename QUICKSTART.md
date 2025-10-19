# VAMedRec - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Open Project in VS Code
```powershell
cd "C:\Users\VHAWRJDRESCF\OneDrive - Department of Veterans Affairs\Documents\GitHub\med-reconciliation"
code .
```

### Step 2: Run Setup Script
```powershell
.\setup.ps1
```

This will:
- ✅ Check Python installation
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Create `.env` file

### Step 3: Add Your API Key
Edit `.env` file:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 4: Run the Application
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start server
python main.py
```

### Step 5: Test It!
Open browser: `http://localhost:5000`

Or test with PowerShell:
```powershell
# Load example request
$example = Get-Content .\examples\example_simple.json | ConvertFrom-Json

# Send request
Invoke-RestMethod -Uri http://localhost:5000/reconcile `
  -Method Post `
  -Body ($example | ConvertTo-Json -Depth 10) `
  -ContentType "application/json"
```

---

## 📋 Common Commands

### Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### Deactivate Virtual Environment
```powershell
deactivate
```

### Run Application
```powershell
python main.py
```

### Test Health Endpoint
```powershell
Invoke-RestMethod -Uri http://localhost:5000/health
```

### Run Tests (once implemented)
```powershell
pytest tests/
```

---

## 🔧 Troubleshooting

### "Python not found"
Install Python 3.9+ from: https://www.python.org/downloads/

### "OPENAI_API_KEY not set"
Edit `.env` file and add your API key.

### "Module not found"
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Port 5000 already in use
Edit `.env` and change:
```
PORT=8000
```

---

## 📖 Next Steps

1. Review `README.md` for full documentation
2. Check `DEVLOG.md` for architecture details
3. Explore `examples/` folder for sample requests
4. Customize `config.py` for your needs

---

## 🏥 VA-Specific Notes

- **Never commit PHI/PII** - it's in `.gitignore`
- Test with **synthetic data only**
- Follow VA security guidelines
- Keep API keys secure

---

## 📞 Support

For issues or questions, refer to project documentation or contact the development team.
