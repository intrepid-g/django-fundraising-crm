# Django Fundraising CRM - Deployment Guide

Complete deployment instructions for production environments.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment-recommended)
4. [Manual Deployment](#manual-deployment)
5. [Database Setup](#database-setup)
6. [Static Files](#static-files)
7. [SSL/HTTPS](#sslhttps)
8. [Monitoring](#monitoring)
9. [Backup Strategy](#backup-strategy)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Server Requirements
- **OS**: Ubuntu 22.04 LTS or Debian 12
- **CPU**: 2+ cores
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 20GB SSD minimum
- **Network**: Static IP, domain name pointed to server

### Required Software
- Docker 24.0+ & Docker Compose v2.0+
- OR Python 3.12+ with uv
- PostgreSQL 15+
- Redis 7+ (optional, for caching/sessions)
- Nginx (reverse proxy)

---

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/intrepid-g/django-fundraising-crm.git
cd django-fundraising-crm
```

### 2. Environment Variables
Create `.env` file:

```bash
# Copy example
cp .env.example .env

# Edit with your values
nano .env
```

**Required Variables:**
```env
# Django
DEBUG=false
SECRET_KEY=your-super-secret-key-here-min-50-chars-long-for-production
ALLOWED_HOSTS=crm.yourdomain.com,localhost

# Database
DATABASE_URL=postgresql://crmuser:crmpassword@db:5432/fundraising_crm

# Optional: Email (for notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Optional: S3/MinIO for file storage
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_ENDPOINT_URL=
```

**Generate Secret Key:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## Docker Deployment (Recommended)

### 1. Quick Start
```bash
# Build and start
docker compose up -d --build

# Run migrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser

# Collect static files
docker compose exec web python manage.py collectstatic --noinput
```

### 2. Verify Installation
```bash
# Check containers
docker compose ps

# View logs
docker compose logs -f web

# Test API curl http://localhost:8000/api/health
```

### 3. Production Docker Compose
Create `compose.prod.yml`:

```yaml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=fundraising_crm
      - POSTGRES_USER=crmuser
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U crmuser -d fundraising_crm"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  web:
    build: .
    command: gunicorn fundraising_crm.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 2
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    environment:
      - DATABASE_URL=postgresql://crmuser:${DB_PASSWORD}@db:5432/fundraising_crm
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

Deploy:
```bash
docker compose -f compose.prod.yml up -d
```

---

## Manual Deployment

### 1. System Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev
sudo apt install -y postgresql-15 postgresql-contrib
sudo apt install -y nginx

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Database Setup
```bash
# Create database
sudo -u postgres psql -c "CREATE DATABASE fundraising_crm;"
sudo -u postgres psql -c "CREATE USER crmuser WITH PASSWORD 'your-password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fundraising_crm TO crmuser;"

# Enable PostGIS (optional, for geolocation)
sudo -u postgres psql -d fundraising_crm -c "CREATE EXTENSION postgis;"
```

### 3. Application Setup
```bash
# Create user
sudo useradd -m -s /bin/bash crm
sudo mkdir -p /opt/fundraising-crm
sudo chown crm:crm /opt/fundraising-crm

# Clone as crm user
sudo -u crm bash -c "
cd /opt/fundraising-crm
git clone https://github.com/intrepid-g/django-fundraising-crm.git .
"

# Install dependencies
sudo -u crm bash -c "
cd /opt/fundraising-crm
uv sync --no-dev
"

# Environment
cp .env.example /opt/fundraising-crm/.env
# Edit .env with production values
```

### 4. Migrations & Static Files
```bash
sudo -u crm bash -c "
cd /opt/fundraising-crm
source .venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
"
```

### 5. Systemd Service
Create `/etc/systemd/system/fundraising-crm.service`:

```ini
[Unit]
Description=Django Fundraising CRM
After=network.target postgresql.service

[Service]
Type=socket
User=crm
Group=crm
WorkingDirectory=/opt/fundraising-crm
ExecStart=/opt/fundraising-crm/.venv/bin/gunicorn \
    --access-logfile - \
    --workers 4 \
    --threads 2 \
    --bind unix:/run/fundraising-crm.sock \
    fundraising_crm.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable fundraising-crm
sudo systemctl start fundraising-crm
```

---

## Database Setup

### Initial Migration
```bash
# Docker
docker compose exec web python manage.py migrate

# Manual
python manage.py migrate
```

### Create Sample Data (Optional)
```bash
# Load demo data
python manage.py loaddata fixtures/demo_data.json

# Or create via shell
python manage.py shell << 'EOF'
from donors.models import Donor
Donor.objects.create(
    first_name="John",
    last_name="Doe",
    email="john@example.com",
    donor_type="individual"
)
EOF
```

---

## Static Files

### Collect Static
```bash
# Docker
docker compose exec web python manage.py collectstatic --noinput

# Manual
python manage.py collectstatic --noinput
```

### Nginx Configuration
Create `/etc/nginx/sites-available/fundraising-crm`:

```nginx
upstream django {
    server unix:/run/fundraising-crm.sock;
}

server {
    listen 80;
    server_name crm.yourdomain.com;
    
    location /static/ {
        alias /opt/fundraising-crm/staticfiles/;
    }
    
    location /media/ {
        alias /opt/fundraising-crm/media/;
    }
    
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/fundraising-crm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## SSL/HTTPS

### Using Certbot (Let's Encrypt)
```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d crm.yourdomain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

### Manual SSL
Place certificates in:
- `/etc/nginx/ssl/crm.yourdomain.com.crt`
- `/etc/nginx/ssl/crm.yourdomain.com.key`

Update nginx config with SSL directives.

---

## Monitoring

### Health Check Endpoint
```bash
curl https://crm.yourdomain.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Log Monitoring
```bash
# Docker
docker compose logs -f web --tail 100

# Manual
sudo journalctl -u fundraising-crm -f
```

### Key Metrics to Monitor
- API response times
- Database connection pool
- Disk space (media uploads)
- Memory usage
- Error rates (500s, 404s)

---

## Backup Strategy

### Database Backup
```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/fundraising-crm"
DB_NAME="fundraising_crm"

mkdir -p $BACKUP_DIR

# PostgreSQL backup
pg_dump -h localhost -U crmuser $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
```

### Media Files Backup
```bash
# Sync to S3 or remote storage
aws s3 sync /opt/fundraising-crm/media/ s3://your-bucket/media/

# Or rsync
rsync -avz /opt/fundraising-crm/media/ backup-server:/backups/media/
```

### Automated Backups (Cron)
```bash
# Daily at 2 AM
0 2 * * * /opt/fundraising-crm/scripts/backup.sh
```

---

## Troubleshooting

### Common Issues

#### 1. Migration Failures
```bash
# Reset migrations (careful - data loss)
python manage.py migrate --run-syncdb

# Or specific app
python manage.py migrate donors zero
python manage.py migrate donors
```

#### 2. Static Files 404
```bash
# Recollect
python manage.py collectstatic --clear --noinput

# Check nginx paths
nginx -t
```

#### 3. Database Connection Refused
```bash
# Check PostgreSQL
sudo systemctl status postgresql
sudo -u postgres psql -c "\l"

# Verify credentials in .env
```

#### 4. Permission Denied (Unix Socket)
```bash
# Fix socket permissions
sudo chown crm:www-data /run/fundraising-crm.sock
sudo chmod 660 /run/fundraising-crm.sock
```

#### 5. Memory Issues
```bash
# Reduce gunicorn workers
# workers = (2 × CPU cores) + 1
# For 2GB RAM, use 2 workers max
```

### Debug Mode (Temporary)
```bash
# Enable debug (DON'T in production long-term)
export DEBUG=true
python manage.py runserver 0.0.0.0:8000
```

### Getting Help
- Check logs: `docker compose logs` or `journalctl`
- API docs: `/api/docs` (when DEBUG=true)
- Django admin: `/admin/`
- GitHub Issues: https://github.com/intrepid-g/django-fundraising-crm/issues

---

## Security Checklist

- [ ] Changed default SECRET_KEY
- [ ] DEBUG=false in production
- [ ] HTTPS enabled with valid certificate
- [ ] Database password is strong
- [ ] Firewall configured (only 80, 443, 22)
- [ ] Regular backups configured
- [ ] Admin URL not default (optional)
- [ ] Rate limiting enabled (nginx)
- [ ] Security headers configured (HSTS, CSP)

---

## Update Procedure

### Docker Update
```bash
# Pull latest
git pull origin main

# Rebuild
docker compose down
docker compose up -d --build

# Migrations
docker compose exec web python manage.py migrate

# Static files
docker compose exec web python manage.py collectstatic --noinput
```

### Manual Update
```bash
cd /opt/fundraising-crm
git pull origin main
source .venv/bin/activate
uv sync --no-dev
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart fundraising-crm
```

---

**Next Steps:** See [QUICKSTART.md](QUICKSTART.md) for first-time setup tasks.
