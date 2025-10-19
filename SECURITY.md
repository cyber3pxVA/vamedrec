# 🔒 Security & Environment File Protection

## ✅ Protection Status

### Git Protection
✅ `.env` files are **EXCLUDED** from Git  
✅ `.env` will **NEVER** be committed to GitHub  
✅ Only `.env.example` (template) is tracked  

### Docker Protection
✅ `.env` files are **EXCLUDED** from Docker builds  
✅ Environment variables must be passed at runtime  
✅ No secrets baked into Docker images  

---

## 📋 Verification Checklist

### Git Exclusion Test
```powershell
# Navigate to project
cd "c:\Users\VHAWRJDRESCF\OneDrive - Department of Veterans Affairs\Documents\GitHub\med-reconciliation"

# Test 1: Check if .env is ignored
git check-ignore .env
# Expected: .env (means it's ignored)

# Test 2: Verify .env is not in status
git status --short | Select-String "\.env"
# Expected: No output (means .env is not tracked)

# Test 3: Try to add .env explicitly (should be ignored)
git add .env
# Expected: Warning or silent ignore
```

### Docker Exclusion Test
```powershell
# Build image and check for .env
docker build -t vamedrec-test .
docker run --rm vamedrec-test ls -la | Select-String "\.env"
# Expected: No .env file in container

# Clean up
docker rmi vamedrec-test
```

---

## 🛡️ Protected Files

The following files are **NEVER** committed or included in Docker images:

### Environment Files
- `.env` - Main environment file (API keys, secrets)
- `.env.local` - Local overrides
- `.env.production` - Production secrets
- `.env.development` - Development secrets
- `.env.test` - Test environment secrets
- `*.env` - Any file ending in .env
- `*.key` - Key files
- `*.secret` - Secret files

### Development Files
- `venv/` - Virtual environment
- `__pycache__/` - Python bytecode
- `.vscode/` - VS Code settings
- `.idea/` - IntelliJ settings

### Sensitive Data
- `*_phi_*` - Protected Health Information
- `*_pii_*` - Personally Identifiable Information
- `patient_data/` - Patient data directory
- `test_data_real/` - Real test data

---

## 📝 Git Ignore Rules

**File:** `.gitignore`

```gitignore
# Environment Variables - CRITICAL: Never commit these!
.env
.env.*
!.env.example
*.env
.env.local
.env.production
.env.development
.env.test
*.key
*.secret
```

**Key Features:**
- `.env.*` - Ignores all .env variants
- `!.env.example` - Exception for the example template
- `*.key` and `*.secret` - Additional secret file protection

---

## 🐳 Docker Ignore Rules

**File:** `.dockerignore`

```dockerignore
# Environment variables - NEVER include in Docker image!
.env
.env.*
!.env.example
*.env
.env.local
.env.production
.env.development
.env.test
*.key
*.secret

# Git
.git/
.gitignore
.github/

# Docker
Dockerfile*
docker-compose*
.dockerignore
```

**Key Features:**
- Same .env protection as .gitignore
- Excludes Git metadata
- Excludes Docker configuration files
- Reduces image size

---

## 🚨 If You Accidentally Commit .env

If you accidentally commit `.env` to Git, follow these steps immediately:

### 1. Remove from Git History
```powershell
# Remove from staging (if not yet committed)
git reset HEAD .env

# If already committed (but not pushed)
git reset --soft HEAD~1

# If already pushed (CRITICAL - rewrites history)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (WARNING: affects all collaborators)
git push --force --all
```

### 2. Rotate All Secrets
**IMMEDIATELY** rotate/regenerate:
- Azure OpenAI API keys
- Docker Hub credentials
- Any other secrets that were in .env

### 3. Notify Security Team
Contact VA security team if sensitive data was exposed.

---

## ✅ Safe Environment Variable Handling

### Development
```powershell
# Copy template
Copy-Item .env.example .env

# Edit with your keys
notepad .env

# Verify it's ignored
git status | Select-String "\.env"
# Should show nothing
```

### Docker Runtime
```powershell
# Method 1: Using .env file (local development)
docker-compose up

# Method 2: Pass variables explicitly
docker run -e OPENAI_API_KEY=$env:OPENAI_API_KEY vamedrec

# Method 3: Use Docker secrets (production)
echo $env:OPENAI_API_KEY | docker secret create openai_key -
```

### Production Deployment
```bash
# Azure Container Instances
az container create \
  --secure-environment-variables \
    OPENAI_API_KEY=$OPENAI_API_KEY \
    AZURE_ENDPOINT=$AZURE_ENDPOINT

# Kubernetes
kubectl create secret generic vamedrec-secrets \
  --from-literal=openai-key=$OPENAI_API_KEY
```

---

## 🔍 Security Audit Commands

### Check for Leaked Secrets
```powershell
# Search Git history for potential secrets
git log --all --full-history -- .env

# Search for API key patterns
git log -p | Select-String "sk-[a-zA-Z0-9]{20,}"

# Check current tracked files
git ls-files | Select-String "\.env"
# Expected: Only .env.example
```

### Docker Image Inspection
```powershell
# Check image layers for secrets
docker history vamedrec:latest

# Inspect running container
docker exec vamedrec ls -la /app/.env
# Expected: File not found
```

---

## 📚 Best Practices

### ✅ DO:
- Use `.env.example` as a template with dummy values
- Keep `.env` in `.gitignore` and `.dockerignore`
- Pass environment variables at runtime
- Use secret management tools in production
- Rotate secrets regularly
- Review changes before committing

### ❌ DON'T:
- Commit `.env` files to Git
- Include secrets in Dockerfile
- Hardcode API keys in source code
- Share `.env` files via email or Slack
- Store secrets in container images
- Use production secrets in development

---

## 🔐 Environment Variables in VAMedRec

### Required Variables
| Variable | Purpose | Location |
|----------|---------|----------|
| `OPENAI_API_KEY` | Azure OpenAI authentication | Never commit |
| `AZURE_ENDPOINT` | Azure OpenAI endpoint URL | Can commit (not secret) |
| `MODEL_NAME` | Model to use (gpt-4o) | Can commit (not secret) |

### Optional Variables
| Variable | Purpose | Default |
|----------|---------|---------|
| `PORT` | Flask server port | 5000 |
| `FLASK_DEBUG` | Debug mode | False |
| `VA_FORMULARY_PATH` | Formulary data path | None |

---

## 📞 Security Contacts

If you discover a security issue:

1. **DO NOT** commit or push
2. **DO NOT** share publicly
3. Contact VA security team immediately
4. Rotate any exposed credentials
5. Document the incident

---

## 🧪 Automated Security Checks

### Pre-commit Hook (Optional)

Create `.git/hooks/pre-commit`:
```bash
#!/bin/sh
# Check for .env files
if git diff --cached --name-only | grep -q "\.env$"; then
    echo "ERROR: Attempting to commit .env file!"
    echo "Please remove .env from commit."
    exit 1
fi

# Check for API keys in code
if git diff --cached -p | grep -qE "(sk-[a-zA-Z0-9]{20,}|api[_-]?key.*=.*['\"])"; then
    echo "WARNING: Possible API key in code!"
    echo "Please review your changes carefully."
    exit 1
fi
```

Make executable:
```powershell
chmod +x .git/hooks/pre-commit
```

---

## ✅ Security Verification Passed

- [x] `.env` in `.gitignore`
- [x] `.env` in `.dockerignore`
- [x] `.env.example` template created
- [x] Git initialized and ignoring .env
- [x] VA-specific sensitive patterns ignored
- [x] Documentation complete

**Status:** 🟢 **SECURE**

Your environment files are properly protected from both Git and Docker! ✅
