# VAMedRec - Docker & CI/CD Setup Guide

## 🐳 Docker Setup

### Prerequisites
- Docker Desktop installed on your machine
- Docker Hub account (for pushing images)

### Local Development with Docker

#### 1. Build the Docker Image
```powershell
cd "C:\Users\VHAWRJDRESCF\OneDrive - Department of Veterans Affairs\Documents\GitHub\med-reconciliation"
docker build -t vamedrec:latest .
```

#### 2. Run with Docker Compose (Recommended)
```powershell
# Make sure you have a .env file with your API key
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

#### 3. Run with Docker CLI
```powershell
# Run with environment variable
docker run -d \
  -p 5000:5000 \
  -e OPENAI_API_KEY=your-api-key-here \
  --name vamedrec \
  vamedrec:latest

# View logs
docker logs -f vamedrec

# Stop the container
docker stop vamedrec
docker rm vamedrec
```

#### 4. Test the Running Container
```powershell
# Health check
curl http://localhost:5000/health

# Or in PowerShell
Invoke-RestMethod -Uri http://localhost:5000/health
```

---

## 🚀 GitHub Actions CI/CD Setup

### Step 1: Create GitHub Repository

1. Go to [github.com](https://github.com)
2. Click "New repository"
3. Name it: `vamedrec` or `med-reconciliation`
4. Initialize without README (since you already have one)
5. Click "Create repository"

### Step 2: Add Docker Hub Secrets to GitHub

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

   **Secret 1:**
   - Name: `DOCKER_USERNAME`
   - Value: Your Docker Hub username

   **Secret 2:**
   - Name: `DOCKER_PASSWORD`
   - Value: Your Docker Hub password or access token (recommended)

#### Creating a Docker Hub Access Token (Recommended)
1. Log in to [hub.docker.com](https://hub.docker.com)
2. Click your username → **Account Settings**
3. Click **Security** → **New Access Token**
4. Name it: `GitHub Actions`
5. Copy the token and use it as `DOCKER_PASSWORD`

### Step 3: Initialize Git and Push to GitHub

```powershell
cd "C:\Users\VHAWRJDRESCF\OneDrive - Department of Veterans Affairs\Documents\GitHub\med-reconciliation"

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: VAMedRec with Docker and GitHub Actions"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR-USERNAME/vamedrec.git

# Push to GitHub
git push -u origin main
```

### Step 4: Verify GitHub Actions

1. Go to your GitHub repository
2. Click the **Actions** tab
3. You should see the workflow running
4. Wait for it to complete (usually 2-5 minutes)
5. Check Docker Hub for your new image

---

## 🔧 Workflow Explained

The `.github/workflows/docker-build.yml` workflow does the following:

1. **Triggers on:**
   - Push to `main` or `master` branch
   - Pull requests
   - Manual trigger (workflow_dispatch)

2. **Steps:**
   - Checks out your code
   - Sets up Docker Buildx (for multi-platform builds)
   - Logs in to Docker Hub
   - Extracts metadata (tags, labels)
   - Builds the Docker image
   - Pushes to Docker Hub with multiple tags

3. **Tags created:**
   - `latest` (on main branch)
   - Branch name (e.g., `main`)
   - SHA prefix (e.g., `main-abc1234`)
   - Version tags (if using semantic versioning)

---

## 🏷️ Docker Image Tags

After successful build, your image will be available at:
```
docker pull yourusername/vamedrec:latest
docker pull yourusername/vamedrec:main
docker pull yourusername/vamedrec:main-abc1234
```

---

## 🔄 Updating Your Application

Every time you push changes to GitHub:

```powershell
# Make your changes
# Then commit and push
git add .
git commit -m "Update feature X"
git push

# GitHub Actions automatically:
# 1. Builds new Docker image
# 2. Pushes to Docker Hub
# 3. Available within minutes
```

---

## 🌐 Deploying to Production

### Option 1: Docker Compose (Simple Server)
```yaml
# On your production server
version: '3.8'
services:
  vamedrec:
    image: yourusername/vamedrec:latest
    ports:
      - "80:5000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: always
```

### Option 2: Kubernetes (Enterprise)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vamedrec
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vamedrec
  template:
    metadata:
      labels:
        app: vamedrec
    spec:
      containers:
      - name: vamedrec
        image: yourusername/vamedrec:latest
        ports:
        - containerPort: 5000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: vamedrec-secrets
              key: openai-api-key
```

### Option 3: Azure Container Instances
```powershell
az container create \
  --resource-group va-medrec \
  --name vamedrec \
  --image yourusername/vamedrec:latest \
  --dns-name-label vamedrec \
  --ports 5000 \
  --environment-variables OPENAI_API_KEY=your-key
```

---

## 🧪 Testing the Docker Image Locally

```powershell
# Pull the image from Docker Hub
docker pull yourusername/vamedrec:latest

# Run it
docker run -d -p 5000:5000 \
  -e OPENAI_API_KEY=your-key \
  yourusername/vamedrec:latest

# Test health endpoint
curl http://localhost:5000/health

# Test reconciliation
curl -X POST http://localhost:5000/reconcile \
  -H "Content-Type: application/json" \
  -d @examples/example_simple.json
```

---

## 📊 Monitoring

The Docker image includes:
- Health check endpoint at `/health`
- Automatic health checks every 30 seconds
- Container restarts on failure
- Logging to stdout/stderr

View logs:
```powershell
docker logs -f vamedrec
```

---

## 🔒 Security Best Practices

1. **Never commit `.env` file** - Already in `.gitignore`
2. **Use Docker secrets** in production
3. **Regularly update base image** - `python:3.11-slim`
4. **Use access tokens** instead of passwords
5. **Scan images** for vulnerabilities
6. **Limit container resources** in production

---

## 🎯 Quick Reference

| Command | Description |
|---------|-------------|
| `docker build -t vamedrec .` | Build image locally |
| `docker-compose up -d` | Start with compose |
| `docker-compose down` | Stop containers |
| `docker logs -f vamedrec` | View logs |
| `docker ps` | List running containers |
| `docker images` | List images |
| `git push` | Trigger CI/CD pipeline |

---

## 🆘 Troubleshooting

### Build Fails
- Check Dockerfile syntax
- Ensure all files exist
- Check base image availability

### Push Fails
- Verify Docker Hub credentials
- Check GitHub secrets are set
- Ensure you have push permissions

### Container Won't Start
- Check logs: `docker logs vamedrec`
- Verify environment variables
- Check port availability

### Health Check Fails
- Verify port 5000 is accessible
- Check application logs
- Test endpoint manually

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Hub](https://hub.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
