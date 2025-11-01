# CI/CD Pipeline Overview

This document provides a visual overview of the NetWorthy CI/CD pipeline.

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DEVELOPER WORKFLOW                          │
└─────────────────────────────────────────────────────────────────────┘

    Developer pushes code
           │
           ▼
    ┌──────────────┐
    │   GitHub     │
    │  Repository  │
    └──────┬───────┘
           │
           ├─────────────────┬─────────────────┬──────────────────┐
           │                 │                 │                  │
           ▼                 ▼                 ▼                  ▼
    ┌─────────────┐   ┌─────────────┐  ┌─────────────┐   ┌──────────────┐
    │   PR/Push   │   │Push to main │  │  Tag v*.*.* │   │   Manual     │
    │  to develop │   │   branch    │  │             │   │   Trigger    │
    └─────┬───────┘   └──────┬──────┘  └──────┬──────┘   └──────┬───────┘
          │                  │                │                  │
          │                  │                │                  │
          ▼                  │                │                  │
    ┌──────────────────────┐ │                │                  │
    │   TEST WORKFLOW      │ │                │                  │
    │                      │ │                │                  │
    │ 1. Setup Python 3.11 │◄┘                │                  │
    │ 2. Start PostgreSQL  │                  │                  │
    │ 3. Install deps      │                  │                  │
    │ 4. Run unit tests    │                  │                  │
    │ 5. Code quality      │                  │                  │
    │ 6. Docker build test │                  │                  │
    └──────────┬───────────┘                  │                  │
               │                              │                  │
               │ ✅ Tests Pass                 │                  │
               │                              │                  │
               ▼                              ▼                  │
          Continue...                  ┌──────────────────────┐  │
                                       │  DOCKER BUILD & PUSH │  │
                                       │                      │  │
                                       │ 1. Multi-arch build  │  │
                                       │    (amd64, arm64)    │  │
                                       │ 2. Push to GHCR      │  │
                                       │ 3. Tag versions      │  │
                                       │    - latest          │  │
                                       │    - v1.0.0          │  │
                                       │    - v1.0            │  │
                                       │    - v1              │  │
                                       │    - main-abc123     │  │
                                       └──────────┬───────────┘  │
                                                  │              │
                                                  ▼              │
                                       Image available at:       │
                                       ghcr.io/jg3233/networthy  │
                                                                 │
                                                  ┌──────────────┘
                                                  │
                                                  ▼
                                       ┌──────────────────────┐
                                       │  DEPLOY WORKFLOW     │
                                       │                      │
                                       │ 1. Connect via SSH   │
                                       │ 2. Backup database   │
                                       │ 3. Pull latest code  │
                                       │ 4. Update .env       │
                                       │ 5. Pull images       │
                                       │ 6. Restart services  │
                                       │ 7. Health check      │
                                       │ 8. Cleanup old imgs  │
                                       └──────────┬───────────┘
                                                  │
                                                  ▼
                                       ┌──────────────────────┐
                                       │  PRODUCTION SERVER   │
                                       │                      │
                                       │  ┌────────────────┐  │
                                       │  │     nginx      │  │
                                       │  │  (Port 80/443) │  │
                                       │  └────────┬───────┘  │
                                       │           │          │
                                       │  ┌────────▼───────┐  │
                                       │  │   Flask App    │  │
                                       │  │  (Gunicorn)    │  │
                                       │  └────────┬───────┘  │
                                       │           │          │
                                       │  ┌────────▼───────┐  │
                                       │  │  PostgreSQL    │  │
                                       │  │   Database     │  │
                                       │  └────────────────┘  │
                                       └──────────────────────┘
```

## Workflow Triggers

### Test Workflow (`test.yml`)
- **Automatic on:** Push to `main` or `develop`
- **Automatic on:** Pull requests to `main` or `develop`
- **Duration:** ~2-3 minutes
- **What it does:**
  - Runs all unit tests
  - Validates code quality
  - Tests Docker builds
  - Ensures PostgreSQL compatibility

### Docker Build & Push (`docker-build.yml`)
- **Automatic on:** Push to `main` branch
- **Automatic on:** Tags matching `v*` (e.g., `v1.0.0`)
- **Automatic on:** GitHub releases
- **Duration:** ~5-7 minutes
- **What it does:**
  - Builds for multiple architectures
  - Pushes to GitHub Container Registry
  - Creates version tags
  - Enables easy deployment with pre-built images

### Deploy Workflow (`deploy.yml`)
- **Manual trigger:** GitHub Actions UI
- **Automatic on:** Tags matching `v*`
- **Duration:** ~3-5 minutes
- **What it does:**
  - Backs up database
  - Deploys latest code
  - Updates Docker containers
  - Verifies deployment health

## Environment Strategy

```
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│  Development │        │   Staging    │        │  Production  │
├──────────────┤        ├──────────────┤        ├──────────────┤
│              │        │              │        │              │
│ Local dev    │  ──►   │ Test server  │  ──►   │ Live server  │
│ Docker       │        │ Full stack   │        │ Full stack   │
│              │        │              │        │              │
│ Trigger:     │        │ Trigger:     │        │ Trigger:     │
│ Manual       │        │ Push develop │        │ Tag release  │
│              │        │ or manual    │        │ or manual    │
└──────────────┘        └──────────────┘        └──────────────┘
```

## Security & Secrets

Required GitHub Secrets for deployment:

| Secret | Purpose | Example |
|--------|---------|---------|
| `SSH_PRIVATE_KEY` | SSH authentication | `-----BEGIN OPENSSH...` |
| `SERVER_HOST` | Target server | `192.168.1.100` |
| `SERVER_USER` | SSH username | `ubuntu` |
| `DEPLOY_PATH` | App directory | `/opt/networthy` |
| `POSTGRES_PASSWORD` | DB password | `secure_password_123` |

## Quick Start Guide

### For Testing
```bash
# Tests run automatically on every PR/push
# No action needed!
```

### For Docker Images
```bash
# Images build automatically on push to main
# Pull the latest:
docker pull ghcr.io/jg3233/networthy:latest
```

### For Deployment

**One-time setup:**
```bash
# 1. Generate SSH key
ssh-keygen -t ed25519 -C "github-deploy" -f ~/.ssh/github_deploy_key

# 2. Copy to server
ssh-copy-id -i ~/.ssh/github_deploy_key.pub user@server

# 3. Add secrets to GitHub
# Go to: Settings → Secrets and variables → Actions
# Add the 5 secrets listed above

# 4. Prepare server
ssh user@server
cd /opt/networthy
git clone https://github.com/JG3233/NetWorthy.git .
cp .env.example .env
nano .env  # Edit credentials
```

**Deploy:**
```bash
# Option 1: Manual via GitHub UI
# Go to Actions → Deploy to Server → Run workflow

# Option 2: Automatic via release tag
git tag v1.0.0
git push origin v1.0.0
# Deployment runs automatically!
```

## Monitoring Workflows

### View Status
- Go to GitHub repository → Actions tab
- See all workflow runs and their status
- Click on any run to see detailed logs

### Status Badges
Add to your README to show build status:
```markdown
![Tests](https://github.com/JG3233/NetWorthy/actions/workflows/test.yml/badge.svg)
![Docker](https://github.com/JG3233/NetWorthy/actions/workflows/docker-build.yml/badge.svg)
```

### Notifications
Configure notifications in GitHub settings:
- Settings → Notifications
- Choose email or web notifications
- Get notified of workflow failures

## Troubleshooting

### Tests Failing
```bash
# Run tests locally first
python -m unittest test_app.py -v

# Check if database is accessible
docker-compose exec db psql -U networthy networthy
```

### Docker Build Failing
```bash
# Test build locally
docker build -t networthy:test .

# Check for file issues
git status  # Ensure all files are committed
```

### Deployment Failing
```bash
# Test SSH connection
ssh -i ~/.ssh/github_deploy_key user@server

# Check server logs
ssh user@server
cd /opt/networthy
docker-compose logs -f
```

## Best Practices

✅ **DO:**
- Run tests locally before pushing
- Use semantic versioning for releases (`v1.0.0`)
- Review deployment logs after each deploy
- Keep SSH keys secure and rotated
- Test in staging before production
- Backup database before major updates

❌ **DON'T:**
- Skip tests by committing `[skip ci]`
- Deploy to production without testing
- Share SSH private keys
- Use weak passwords in secrets
- Delete database backups
- Force push to main branch

## Advanced: Custom Workflows

### Add Staging Environment

Create `.github/workflows/deploy-staging.yml`:
```yaml
name: Deploy to Staging

on:
  push:
    branches: [ develop ]

jobs:
  deploy-staging:
    # Same as deploy.yml but with staging secrets
```

### Add Automated Backups

Create `.github/workflows/backup.yml`:
```yaml
name: Database Backup

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - name: Backup database
        # SSH to server and run backup
```

### Add Performance Tests

Add to `test.yml`:
```yaml
- name: Performance tests
  run: |
    pip install locust
    locust -f tests/performance.py --headless -u 100 -r 10
```

## Workflow Costs

GitHub Actions usage:
- **Free tier:** 2,000 minutes/month for private repos
- **Public repos:** Unlimited
- **These workflows use:** ~10 minutes per full deployment
- **Estimated usage:** 200-300 minutes/month for active development

## Next Steps

1. ✅ CI/CD pipeline is ready to use
2. 🔧 Set up GitHub Secrets for deployment
3. 📋 Test the workflows by creating a PR
4. 🚀 Deploy to your VM
5. 📊 Monitor via GitHub Actions dashboard

For detailed documentation, see [.github/workflows/README.md](.github/workflows/README.md)
