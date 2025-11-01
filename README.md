# NetWorthy

[![Tests](https://github.com/JG3233/NetWorthy/actions/workflows/test.yml/badge.svg)](https://github.com/JG3233/NetWorthy/actions/workflows/test.yml)
[![Docker Build](https://github.com/JG3233/NetWorthy/actions/workflows/docker-build.yml/badge.svg)](https://github.com/JG3233/NetWorthy/actions/workflows/docker-build.yml)
[![License](https://img.shields.io/github/license/JG3233/NetWorthy)](LICENSE)

A production-ready Net Worth tracking application inspired by the Money Guy show, built with Flask, PostgreSQL, and nginx.

## Description

NetWorthy helps you track and analyze your net worth over time. Track assets (cash, investments, business interests, property), liabilities, and income across multiple years. Get insights based on Money Guy wealth accumulation metrics (PAW/AAW/UAW).

## Features

- **Multi-year tracking** - Track your financial data across years
- **Asset categorization** - Cash, investments (pre-tax/tax-free/after-tax), business interests, property
- **Liability tracking** - Track debts and loans
- **Income tracking** - Monitor income sources over time
- **Wealth analysis** - Analyze your wealth accumulation status (PAW/AAW/UAW)
- **Production-ready** - PostgreSQL database with nginx reverse proxy
- **Docker deployment** - Easy deployment with docker-compose

## Architecture

The application uses a modern, production-ready stack:

- **nginx** - Reverse proxy, static file serving, SSL termination ready
- **Flask** - Python web application framework
- **PostgreSQL** - Production-grade relational database
- **Gunicorn** - WSGI HTTP server for Python
- **Docker** - Containerization for easy deployment

## Quick Start

### Prerequisites

- Docker and Docker Compose installed on your system
- Git (to clone the repository)

### Deployment Steps

1. **Clone the repository:**
```bash
git clone https://github.com/JG3233/NetWorthy.git
cd NetWorthy
```

2. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env and change the default passwords!
nano .env  # or use your preferred editor
```

**IMPORTANT:** Change the default passwords in `.env` before deploying to production!

3. **Start the application:**
```bash
docker-compose up -d
```

This will start three containers:
- `networthy-db` - PostgreSQL database
- `networthy-app` - Flask application
- `networthy-nginx` - nginx reverse proxy

4. **Access the application:**
- Open your browser to `http://localhost` or `http://your-vm-ip`
- The application will be accessible through nginx on port 80

5. **Check status:**
```bash
docker-compose ps
docker-compose logs -f  # View logs
```

### Stopping the Application

```bash
docker-compose down  # Stop and remove containers
docker-compose down -v  # Stop and remove containers AND delete database (⚠️ data loss!)
```

## Migrating from JSON Version

If you have existing data in `net_worth_history.json` from an older version:

1. Place your `net_worth_history.json` file in the project directory
2. Start the containers: `docker-compose up -d`
3. Run the migration script:
```bash
docker-compose exec app python migrate_json_to_postgres.py
```

Your data will be imported into PostgreSQL. The JSON file is kept as a backup.

## CI/CD Pipeline

NetWorthy includes a complete GitHub Actions CI/CD pipeline for automated testing, building, and deployment.

### Automated Testing

Every push and pull request automatically:
- ✅ Runs unit tests with PostgreSQL
- ✅ Checks code style with flake8
- ✅ Tests Docker image builds
- ✅ Validates docker-compose configuration

### Docker Image Publishing

Pushes to `main` branch automatically:
- 🐳 Build multi-architecture Docker images (amd64, arm64)
- 📦 Push to GitHub Container Registry
- 🏷️ Tag with version numbers and `latest`

**Using pre-built images:**
```bash
# Pull the latest image
docker pull ghcr.io/jg3233/networthy:latest

# Or update docker-compose.yml:
services:
  app:
    image: ghcr.io/jg3233/networthy:latest
    # Remove 'build: .' line
```

### Automated Deployment

Deploy to your VM with one click or automatically on release:

**Setup (one-time):**
1. Generate SSH key: `ssh-keygen -t ed25519 -f ~/.ssh/github_deploy_key`
2. Copy to server: `ssh-copy-id -i ~/.ssh/github_deploy_key.pub user@server`
3. Add secrets to GitHub (Settings → Secrets → Actions):
   - `SSH_PRIVATE_KEY` - Your private key
   - `SERVER_HOST` - Server IP/hostname
   - `SERVER_USER` - SSH username
   - `DEPLOY_PATH` - App path (e.g., `/opt/networthy`)
   - `POSTGRES_PASSWORD` - Database password

**Deploy:**
- Go to Actions → Deploy to Server → Run workflow
- Or create a release tag: `git tag v1.0.0 && git push origin v1.0.0`

The deployment workflow automatically:
- 💾 Backs up database
- ⬇️ Pulls latest code
- 🐳 Updates containers
- ✅ Verifies health

See [.github/workflows/README.md](.github/workflows/README.md) for detailed CI/CD documentation.

## Configuration

### Environment Variables

Configure the application by editing `.env`:

```env
# Database
POSTGRES_DB=networthy
POSTGRES_USER=networthy
POSTGRES_PASSWORD=your_secure_password_here

# Flask
FLASK_ENV=production
SECRET_KEY=your_secret_key_here
```

### Port Configuration

By default, the application uses:
- Port 80 (HTTP) - nginx
- Port 443 (HTTPS) - nginx (when SSL is configured)
- Port 5432 - PostgreSQL (exposed for development, remove in production)

To change ports, edit `docker-compose.yml`:
```yaml
nginx:
  ports:
    - "8080:80"  # Use port 8080 instead of 80
```

## HTTPS/SSL Configuration

To enable HTTPS:

1. **Obtain SSL certificates** (using Let's Encrypt, self-signed, or from a CA)

2. **Create SSL directory:**
```bash
mkdir ssl
cp /path/to/your/cert.pem ssl/
cp /path/to/your/key.pem ssl/
```

3. **Uncomment HTTPS section in nginx.conf**

4. **Update docker-compose.yml** to mount SSL directory:
```yaml
nginx:
  volumes:
    - ./ssl:/etc/nginx/ssl:ro
```

5. **Restart nginx:**
```bash
docker-compose restart nginx
```

## VM Deployment

### Deploying on a Virtual Machine

1. **Install Docker and Docker Compose:**
```bash
# For Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install docker-compose-plugin
```

2. **Clone and configure:**
```bash
git clone https://github.com/JG3233/NetWorthy.git
cd NetWorthy
cp .env.example .env
nano .env  # Update passwords
```

3. **Configure firewall:**
```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

4. **Start the application:**
```bash
docker-compose up -d
```

5. **Set up automatic start on reboot:**

The `restart: unless-stopped` policy in docker-compose.yml ensures containers restart automatically.

To enable Docker to start on boot:
```bash
sudo systemctl enable docker
```

## Database Backup and Restore

### Backup

Create a backup of your PostgreSQL database:

```bash
# Backup to file
docker-compose exec -T db pg_dump -U networthy networthy > backup_$(date +%Y%m%d).sql

# Backup entire database including users
docker-compose exec -T db pg_dumpall -U networthy > backup_full_$(date +%Y%m%d).sql
```

### Restore

Restore from a backup:

```bash
# Restore database
docker-compose exec -T db psql -U networthy networthy < backup_20241101.sql
```

### Automated Backups

Set up a cron job for daily backups:

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 2 AM)
0 2 * * * cd /path/to/NetWorthy && docker-compose exec -T db pg_dump -U networthy networthy > backups/backup_$(date +\%Y\%m\%d).sql
```

## Development

### Running Tests

```bash
# Install dependencies locally
pip install -r requirements.txt

# Run tests
python -m unittest test_app.py -v
```

### Local Development (without Docker)

1. **Install PostgreSQL locally**

2. **Set up Python environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure database:**
```bash
createdb networthy
export DATABASE_URL=postgresql://localhost/networthy
```

4. **Run the application:**
```bash
python app.py
```

Access at `http://localhost:5000`

## Monitoring and Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f db
docker-compose logs -f nginx
```

### Check Container Health

```bash
docker-compose ps
```

All containers should show "healthy" status.

### Database Console

Access PostgreSQL console:

```bash
docker-compose exec db psql -U networthy networthy
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart app
```

## Updating the Application

To update to a new version:

```bash
# 1. Backup your database first!
docker-compose exec -T db pg_dump -U networthy networthy > backup_before_update.sql

# 2. Pull latest changes
git pull

# 3. Rebuild and restart
docker-compose down
docker-compose up -d --build

# 4. Check logs
docker-compose logs -f
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs app

# Check database connection
docker-compose exec app python -c "from app import db; print(db.engine.url)"
```

### Database connection errors

```bash
# Verify database is running
docker-compose exec db pg_isready -U networthy

# Check database logs
docker-compose logs db
```

### Reset Everything

⚠️ **WARNING: This deletes all data!**

```bash
docker-compose down -v
docker-compose up -d
```

## Security Considerations

- ✅ Change default passwords in `.env`
- ✅ Use strong passwords for production
- ✅ Don't commit `.env` to version control (already in `.gitignore`)
- ✅ Enable HTTPS/SSL for production deployments
- ✅ Keep Docker images updated (`docker-compose pull`)
- ✅ Regular database backups
- ✅ Limit PostgreSQL port exposure in production (remove port mapping)

## Performance Tuning

### For larger deployments:

1. **Increase Gunicorn workers** (in docker-compose.yml):
```yaml
command: gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

2. **Optimize PostgreSQL** (add to docker-compose.yml db service):
```yaml
command: postgres -c shared_buffers=256MB -c max_connections=200
```

3. **Enable nginx caching** (edit nginx.conf)

## Support and Contributing

- Report issues: https://github.com/JG3233/NetWorthy/issues
- See DATABASE_OPTIONS.md for database architecture decisions
- Original JSON version available in `app_json_backup.py`

## License

See LICENSE file for details.

## Credits

Inspired by the Money Guy show's net worth tracking methodology.
