# 🚀 VAMedRec Deployment Checklist

## ✅ Pre-Deployment Checklist

### Environment Setup
- [x] Virtual environment created (`venv/`)
- [x] Dependencies installed from `requirements.txt`
- [x] `.env` file created from `.env.example`
- [ ] **Azure API key added to `.env` file** ⚠️ REQUIRED

### Code Quality
- [x] All core modules present
- [x] Configuration file updated for Azure OpenAI
- [x] Health endpoint implemented
- [x] Error handling in place

### Docker Setup
- [x] `Dockerfile` created
- [x] `docker-compose.yml` configured
- [x] `.dockerignore` optimized
- [ ] Docker image tested locally

### CI/CD Pipeline
- [x] GitHub Actions workflow created
- [ ] GitHub repository created
- [ ] Docker Hub account ready
- [ ] GitHub secrets configured:
  - [ ] `DOCKER_USERNAME`
  - [ ] `DOCKER_PASSWORD`

---

## 🔑 Required Actions

### 1. Add Azure API Key
**Priority: HIGH**

Edit `.env` file:
```bash
OPENAI_API_KEY=your-actual-azure-api-key-here
```

### 2. Test Locally
```powershell
# Start the server
.\venv\Scripts\Activate.ps1
python main.py

# Test health endpoint
Invoke-RestMethod -Uri http://localhost:5000/health

# Test with sample data
$body = Get-Content examples/example_simple.json | ConvertFrom-Json
Invoke-RestMethod -Uri http://localhost:5000/reconcile -Method Post -Body ($body | ConvertTo-Json -Depth 10) -ContentType "application/json"
```

### 3. Set Up GitHub Repository
```powershell
# Initialize (if needed)
git init

# Configure user
git config user.name "Your Name"
git config user.email "your.email@va.gov"

# Add files
git add .

# Commit
git commit -m "feat: Initial VAMedRec setup with Azure OpenAI and Docker"

# Add remote (replace with your URL)
git remote add origin https://github.com/YOUR-USERNAME/vamedrec.git

# Push
git push -u origin main
```

### 4. Configure GitHub Secrets
1. Go to: `https://github.com/YOUR-USERNAME/vamedrec/settings/secrets/actions`
2. Click "New repository secret"
3. Add secrets:
   - **DOCKER_USERNAME**: Your Docker Hub username
   - **DOCKER_PASSWORD**: Your Docker Hub access token

### 5. Test Docker Locally
```powershell
# Build image
docker build -t vamedrec:latest .

# Run container (add your API key)
docker run -d -p 5000:5000 -e AZURE_ENDPOINT=https://spd-prod-openai-va-apim.azure-api.us/api -e OPENAI_API_KEY=your-key -e MODEL_NAME=gpt-4o vamedrec:latest

# Check health
Invoke-RestMethod -Uri http://localhost:5000/health

# View logs
docker logs <container-id>

# Stop container
docker stop <container-id>
```

---

## 📋 Deployment Environments

### Development (Current)
- [x] Running on localhost:5000
- [x] Using virtual environment
- [ ] API key configured
- [ ] Tested with sample data

### Docker Local
- [ ] Image built successfully
- [ ] Container runs without errors
- [ ] Health check passes
- [ ] API endpoints working

### Docker Hub
- [ ] Account created
- [ ] Repository created (e.g., `yourusername/vamedrec`)
- [ ] Image pushed successfully
- [ ] Tags configured (latest, version)

### Production Options

#### Option A: Azure Container Instances
```bash
az container create \
  --resource-group va-medrec-prod \
  --name vamedrec-prod \
  --image yourusername/vamedrec:latest \
  --dns-name-label vamedrec-prod \
  --ports 5000 \
  --secure-environment-variables \
    AZURE_ENDPOINT=$AZURE_ENDPOINT \
    OPENAI_API_KEY=$OPENAI_API_KEY \
    MODEL_NAME=gpt-4o
```

#### Option B: Azure App Service
```bash
az webapp create \
  --resource-group va-medrec-prod \
  --plan va-medrec-plan \
  --name vamedrec-api \
  --deployment-container-image-name yourusername/vamedrec:latest
```

#### Option C: Kubernetes (AKS)
See `DOCKER.md` for Kubernetes deployment manifests

---

## 🧪 Testing Checklist

### Unit Tests
- [ ] Test medication normalization
- [ ] Test safety checks
- [ ] Test ledger validation
- [ ] Test LLM integration (with mock)

### Integration Tests
- [ ] Test /health endpoint
- [ ] Test /reconcile endpoint
- [ ] Test with sample simple reconciliation
- [ ] Test with sample comprehensive reconciliation
- [ ] Test error handling
- [ ] Test with invalid data

### Load Tests
- [ ] Test concurrent requests
- [ ] Test response times
- [ ] Test memory usage
- [ ] Test Azure API rate limits

---

## 🔒 Security Checklist

### Code Security
- [x] `.env` file in `.gitignore`
- [x] No hardcoded credentials
- [x] Virtual environment excluded from git
- [x] Input validation in place
- [ ] Security scan completed

### Azure Security
- [ ] API key rotated regularly
- [ ] Least privilege access configured
- [ ] Network security groups configured
- [ ] Logging enabled
- [ ] Monitoring alerts set up

### Docker Security
- [x] Multi-stage build (minimal image size)
- [x] Non-root user in container
- [ ] Image scanned for vulnerabilities
- [ ] Secrets not in image layers

---

## 📊 Monitoring & Observability

### Health Monitoring
- [x] `/health` endpoint implemented
- [ ] Uptime monitoring configured
- [ ] Alert thresholds set
- [ ] On-call rotation defined

### Logging
- [ ] Application logs configured
- [ ] Centralized logging (e.g., Azure Monitor)
- [ ] Log retention policy defined
- [ ] Log analysis tools configured

### Metrics
- [ ] Response time tracking
- [ ] Error rate monitoring
- [ ] API usage metrics
- [ ] Azure OpenAI usage tracking

---

## 📝 Documentation Checklist

- [x] README.md complete
- [x] DOCKER.md with deployment guide
- [x] API documentation in home page
- [x] .env.example with all variables
- [x] Setup instructions clear
- [ ] Architecture diagram created
- [ ] Runbook for operations
- [ ] Incident response procedures

---

## 🎯 Go-Live Checklist

### Final Verification
- [ ] All tests passing
- [ ] Documentation reviewed
- [ ] Security review completed
- [ ] Performance benchmarks met
- [ ] Backup strategy defined
- [ ] Rollback plan documented

### Stakeholder Approval
- [ ] Technical review approved
- [ ] Security review approved
- [ ] Compliance review approved
- [ ] Clinical team sign-off
- [ ] VA approval obtained

### Launch
- [ ] Production deployment successful
- [ ] Health checks passing
- [ ] Monitoring active
- [ ] Team notified
- [ ] Success criteria met

---

## 🆘 Rollback Plan

If issues occur during deployment:

1. **Immediate Actions:**
   ```bash
   # Stop the service
   docker-compose down
   # or
   az container delete --name vamedrec-prod
   ```

2. **Restore Previous Version:**
   ```bash
   docker pull yourusername/vamedrec:previous-tag
   docker run -d -p 5000:5000 yourusername/vamedrec:previous-tag
   ```

3. **Notify Team:**
   - Alert on-call engineer
   - Update status page
   - Communicate with stakeholders

4. **Post-Mortem:**
   - Document what went wrong
   - Identify root cause
   - Update deployment procedures

---

## 📞 Support Contacts

| Role | Contact | Responsibility |
|------|---------|----------------|
| Lead Developer | TBD | Code issues, features |
| DevOps Engineer | TBD | Deployment, infrastructure |
| Security Officer | TBD | Security reviews |
| Clinical SME | TBD | Clinical validation |

---

## 📅 Timeline

- [x] **Day 1**: Environment setup, Azure config
- [ ] **Day 2**: API key setup, local testing
- [ ] **Day 3**: Docker testing, GitHub setup
- [ ] **Day 4**: CI/CD pipeline testing
- [ ] **Day 5**: Security review
- [ ] **Week 2**: Production deployment
- [ ] **Week 3**: Monitoring and optimization

---

**Status:** 🟡 In Progress  
**Next Step:** Add Azure API key and test with real data  
**Blocker:** None  
**Risk Level:** Low
