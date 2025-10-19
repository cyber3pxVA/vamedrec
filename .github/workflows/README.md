# GitHub Actions Workflow

This directory contains the CI/CD pipeline configuration for VAMedRec.

## Workflow: Docker Build and Push

**File:** `docker-build.yml`

### What It Does

Automatically builds and publishes a Docker image to Docker Hub whenever you push code to the repository.

### Triggers

- Push to `main` or `master` branch
- Pull requests to `main` or `master` branch
- Manual trigger via GitHub UI (workflow_dispatch)

### Steps

1. **Checkout Code** - Downloads your repository code
2. **Set Up Docker Buildx** - Configures advanced Docker build capabilities
3. **Log in to Docker Hub** - Authenticates using secrets
4. **Extract Metadata** - Generates image tags and labels
5. **Build and Push** - Creates Docker image and uploads to Docker Hub

### Image Tags

The workflow creates multiple tags for each build:

- `latest` - Always points to the most recent build from main branch
- `main` - Tracks the main branch
- `main-abc1234` - Includes the git commit SHA
- `v1.0.0` - If you use semantic versioning tags

### Required Secrets

Set these up in GitHub repository settings:

1. Go to **Settings → Secrets and variables → Actions**
2. Add these secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `DOCKER_USERNAME` | Your Docker Hub username | `yourusername` |
| `DOCKER_PASSWORD` | Docker Hub access token | `dckr_pat_abc123...` |

### Creating a Docker Hub Access Token

1. Log in to [hub.docker.com](https://hub.docker.com)
2. Click your username → **Account Settings**
3. Go to **Security** → **New Access Token**
4. Name: `GitHub Actions`
5. Permissions: **Read, Write, Delete**
6. Copy the token (you won't see it again!)
7. Use this as `DOCKER_PASSWORD` in GitHub secrets

### Viewing Build Status

After pushing code:

1. Go to your GitHub repository
2. Click the **Actions** tab
3. Click on your workflow run
4. View real-time logs and status

### Build Output

After successful build, your image will be available at:

```bash
docker pull yourusername/vamedrec:latest
```

### Troubleshooting

#### Build Fails - Authentication Error
- Check that `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets are set correctly
- Verify your Docker Hub access token is still valid
- Ensure the token has write permissions

#### Build Fails - Dockerfile Error
- Review the build logs in GitHub Actions
- Test the build locally: `docker build -t vamedrec:test .`
- Fix any errors in Dockerfile

#### Image Not Appearing in Docker Hub
- Check that the workflow completed successfully
- Verify the repository name matches: `yourusername/vamedrec`
- Ensure you have push permissions to the Docker Hub repository

### Manual Trigger

To manually trigger a build without pushing code:

1. Go to **Actions** tab
2. Click **Build and Push VAMedRec Docker Image**
3. Click **Run workflow**
4. Select branch
5. Click **Run workflow**

### Customization

#### Change Docker Hub Repository Name

Edit `docker-build.yml`, line 36:
```yaml
images: ${{ secrets.DOCKER_USERNAME }}/your-new-name
```

#### Add Additional Tags

Edit the `tags:` section:
```yaml
tags: |
  type=ref,event=branch
  type=ref,event=pr
  type=semver,pattern={{version}}
  type=raw,value=production  # Add custom tag
```

#### Build for Multiple Platforms

Add this to the build step:
```yaml
platforms: linux/amd64,linux/arm64
```

### Best Practices

✅ Use access tokens instead of passwords  
✅ Rotate tokens regularly  
✅ Use semantic versioning for releases  
✅ Test Docker builds locally before pushing  
✅ Monitor build times and optimize if needed  
✅ Use build caching for faster builds  

### Cache Strategy

The workflow uses Docker layer caching to speed up builds:

- **Cache source:** Previous build layers
- **Cache destination:** Docker registry
- **Mode:** `max` (caches all layers)

This can reduce build time from 5+ minutes to under 1 minute on subsequent builds.

### Security

- Secrets are never exposed in logs
- Docker credentials are masked in output
- Access tokens can be revoked anytime
- Multi-stage builds minimize attack surface
- Images are scanned for vulnerabilities (optional, can be added)

### Adding Vulnerability Scanning

To add security scanning, insert this step before build:

```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ secrets.DOCKER_USERNAME }}/vamedrec:latest
    format: 'sarif'
    output: 'trivy-results.sarif'
```

### Notifications

To get notified of build results:

1. Enable GitHub notifications for your repository
2. Or add a Slack/Teams notification step
3. Or use GitHub Actions status badges in README

### Status Badge

Add this to your README.md to show build status:

```markdown
![Docker Build](https://github.com/YOUR-USERNAME/vamedrec/actions/workflows/docker-build.yml/badge.svg)
```

---

## Additional Workflows

You can add more workflows for:

- **Testing** (`test.yml`) - Run unit tests on every push
- **Linting** (`lint.yml`) - Check code quality
- **Security** (`security.yml`) - Security scans
- **Deployment** (`deploy.yml`) - Auto-deploy to production

---

**Need Help?**

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Docker Hub](https://hub.docker.com/)
