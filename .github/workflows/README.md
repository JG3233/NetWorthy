# GitHub Actions CI/CD Workflows

This directory contains GitHub Actions workflows for automated testing, building, and deployment of NetWorthy.

## Workflows

### 1. Tests (`test.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**What it does:**
- ✅ Sets up Python 3.11 environment
- ✅ Starts PostgreSQL test database
- ✅ Installs dependencies
- ✅ Runs unit tests with PostgreSQL
- ✅ Checks code style with flake8
- ✅ Tests Docker image build
- ✅ Validates docker-compose configuration

**No setup required** - runs automatically on every PR and push.

---

### 2. Docker Build and Push (`docker-build.yml`)

**Triggers:**
- Push to `main` branch
- Creating version tags (e.g., `v1.0.0`)
- Publishing releases

**What it does:**
- 🐳 Builds Docker image for multiple architectures (amd64, arm64)
- 📦 Pushes to GitHub Container Registry (ghcr.io)
- 🏷️ Tags images with:
  - Branch name (e.g., `main`)
  - Git SHA (e.g., `main-abc1234`)
  - Semantic version tags (e.g., `v1.0.0`, `v1.0`, `v1`)
  - `latest` tag for main branch
- ✅ Creates build attestation for security

**No setup required** - automatically uses GitHub's built-in `GITHUB_TOKEN`.

**Using the published images:**
```bash
# Pull the latest image
docker pull ghcr.io/jg3233/networthy:latest

# Pull a specific version
docker pull ghcr.io/jg3233/networthy:v1.0.0

# Update docker-compose.yml to use the pre-built image:
services:
  app:
    image: ghcr.io/jg3233/networthy:latest
    # Remove the 'build: .' line
```

---

### 3. Deploy to Server (`deploy.yml`)

**Triggers:**
- Manual trigger via GitHub Actions UI
- Creating version tags (e.g., `v1.0.0`)

**What it does:**
- 🔐 Connects to your server via SSH
- 💾 Creates database backup before deployment
- ⬇️ Pulls latest code changes
- 🐳 Updates Docker containers
- ✅ Verifies deployment health
- 🧹 Cleans up old Docker images

**Setup Required:**

#### Step 1: Generate SSH Key

On your local machine:
```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy_key
```

Copy the public key to your server:
```bash
ssh-copy-id -i ~/.ssh/github_deploy_key.pub user@your-server.com
```

#### Step 2: Add GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `SSH_PRIVATE_KEY` | Private SSH key content | Contents of `~/.ssh/github_deploy_key` |
| `SERVER_HOST` | Your server hostname/IP | `192.168.1.100` or `server.example.com` |
| `SERVER_USER` | SSH username | `ubuntu` or `root` |
| `DEPLOY_PATH` | Path to app on server | `/opt/networthy` |
| `POSTGRES_PASSWORD` | Database password | `your_secure_password` |

**To get the private key content:**
```bash
cat ~/.ssh/github_deploy_key
```

Copy everything including the `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----` lines.

#### Step 3: Prepare Your Server

On your server:
```bash
# Create deployment directory
sudo mkdir -p /opt/networthy
sudo chown $USER:$USER /opt/networthy
cd /opt/networthy

# Clone the repository
git clone https://github.com/JG3233/NetWorthy.git .

# Create .env file
cp .env.example .env
nano .env  # Edit with your passwords
```

#### Step 4: Deploy

**Manual deployment via GitHub UI:**
1. Go to Actions tab in GitHub
2. Click "Deploy to Server" workflow
3. Click "Run workflow"
4. Select environment (production/staging)
5. Click "Run workflow"

**Automatic deployment on release:**
1. Create a tag: `git tag v1.0.0`
2. Push tag: `git push origin v1.0.0`
3. Deployment runs automatically

---

## Workflow Status Badges

Add these to your README.md to show workflow status:

```markdown
![Tests](https://github.com/JG3233/NetWorthy/actions/workflows/test.yml/badge.svg)
![Docker Build](https://github.com/JG3233/NetWorthy/actions/workflows/docker-build.yml/badge.svg)
```

---

## Environment Setup

### For Production Deployment

Create a `production` environment in GitHub:

1. Go to Settings → Environments → New environment
2. Name: `production`
3. Add protection rules:
   - ✅ Required reviewers (optional)
   - ✅ Wait timer (optional)
4. Add environment secrets (same as repository secrets above)

### For Staging Deployment

Repeat the same process for a `staging` environment with different server details.

---

## Customization

### Change Deployment Trigger

Edit `.github/workflows/deploy.yml`:

```yaml
# Deploy on every push to main (not recommended for production)
on:
  push:
    branches: [ main ]

# Deploy only on manual trigger (recommended)
on:
  workflow_dispatch:

# Deploy on tags only
on:
  push:
    tags:
      - 'v*'
```

### Add Notifications

You can add Slack, Discord, or email notifications:

```yaml
- name: Notify Slack
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Run Different Tests

Edit `.github/workflows/test.yml`:

```yaml
- name: Run integration tests
  run: |
    python -m pytest tests/integration/

- name: Run security scan
  run: |
    pip install bandit
    bandit -r . -f json -o bandit-report.json
```

---

## Troubleshooting

### SSH Connection Fails

```bash
# Test SSH connection locally
ssh -i ~/.ssh/github_deploy_key user@server.com

# Check SSH key permissions
chmod 600 ~/.ssh/github_deploy_key

# Add verbose output to workflow
ssh -vvv -i ~/.ssh/deploy_key ...
```

### Docker Build Fails

- Check Dockerfile syntax
- Ensure all COPY commands reference existing files
- Check for sufficient disk space on runner
- Review build logs in GitHub Actions

### Deployment Fails

- Check server disk space: `df -h`
- Check Docker status: `docker ps`
- Check logs: `docker-compose logs`
- Verify .env file exists and has correct values

### Tests Fail

- Check if tests pass locally first
- Ensure test database connection is correct
- Review test output in GitHub Actions logs
- Check for missing dependencies

---

## Security Best Practices

✅ **DO:**
- Use GitHub Secrets for sensitive data
- Rotate SSH keys regularly
- Use environment-specific secrets
- Review deployment logs
- Set up required reviewers for production deploys
- Use semantic versioning for releases

❌ **DON'T:**
- Commit secrets to repository
- Use the same SSH key for multiple servers
- Deploy to production without testing
- Skip database backups before deployment
- Use weak passwords

---

## Advanced: Multi-Environment Setup

For a complete production setup with staging:

```yaml
# .github/workflows/deploy.yml
jobs:
  deploy-staging:
    if: github.ref == 'refs/heads/develop'
    environment: staging
    # ... deploy to staging server

  deploy-production:
    if: startsWith(github.ref, 'refs/tags/v')
    environment: production
    needs: deploy-staging  # Only deploy to prod after staging succeeds
    # ... deploy to production server
```

---

## Monitoring Deployments

After deployment, monitor:

```bash
# On your server
docker-compose ps              # Check container status
docker-compose logs -f app     # Watch application logs
docker-compose logs -f db      # Watch database logs
docker stats                   # Monitor resource usage
```

---

## Rollback

If a deployment fails:

```bash
# SSH into server
ssh user@server.com

cd /opt/networthy

# Find previous commit
git log --oneline

# Rollback to previous version
git checkout <previous-commit-hash>

# Restore database backup if needed
docker-compose exec -T db psql -U networthy networthy < backup_20241101_120000.sql

# Restart containers
docker-compose down
docker-compose up -d
```

Or use the GitHub Actions UI to re-run a previous successful deployment.
