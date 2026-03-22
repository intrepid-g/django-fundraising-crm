# Django Fundraising CRM

A production-ready fundraising CRM built with Django 5.2 and React.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/intrepid-g/django-fundraising-crm.git
cd django-fundraising-crm

# Docker setup
docker-compose up -d

# Or local setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Features

- Donor management with tags and segments
- Donation tracking (one-time, recurring, pledges)
- Campaign management
- Event management
- Communication history
- Reporting and analytics

## Architecture

- **Backend:** Django 5.2 + django-ninja (API)
- **Frontend:** React 18 + Vite
- **Database:** PostgreSQL
- **Cache:** Redis
- **Queue:** Celery + Redis

## Project Structure

```
backend/           # Django project
  apps/
    donors/        # Donor management
    donations/     # Donation tracking
    campaigns/     # Campaign management
    events/        # Event management
    communications/# Email/SMS history
    reports/       # Analytics and reports
frontend/          # React SPA
docker/           # Docker configs
```

## Development

Built via the 7-habits autonomous agent framework.
