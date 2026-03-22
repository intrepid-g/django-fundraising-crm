# Django Fundraising CRM - Quick Start Guide

Get up and running in 5 minutes.

## Prerequisites
- Docker & Docker Compose installed
- Git installed
- Terminal/Command line access

---

## 1. Clone & Launch (2 minutes)

```bash
# Clone repository
git clone https://github.com/intrepid-g/django-fundraising-crm.git
cd django-fundraising-crm

# Start services
docker compose up -d

# Run migrations
docker compose exec web python manage.py migrate

# Create admin user
docker compose exec web python manage.py createsuperuser
```

**Access the app:**
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

---

## 2. First Steps (3 minutes)

### Create Your First Donor
```bash
# Using curl
curl -X POST http://localhost:8000/api/donors/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@example.com",
    "donor_type": "individual"
  }'
```

Or use the Django Admin:
1. Go to http://localhost:8000/admin/
2. Login with superuser credentials
3. Click "Donors" → "Add Donor"

### Record a Donation
```bash
curl -X POST http://localhost:8000/api/donations/ \
  -H "Content-Type: application/json" \
  -d '{
    "donor_id": 1,
    "amount": 100.00,
    "donation_type": "one_time"
  }'
```

### Create a Campaign
```bash
curl -X POST http://localhost:8000/api/campaigns/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Spring Fundraiser 2024",
    "goal_amount": 50000,
    "start_date": "2024-03-01",
    "end_date": "2024-05-31"
  }'
```

---

## 3. Common Tasks

### View All Donors
```bash
curl http://localhost:8000/api/donors/
```

### Search Donors
```bash
curl -X POST http://localhost:8000/api/donors/search \
  -H "Content-Type: application/json" \
  -d '{"query": "jane"}'
```

### Get Donor Stats
```bash
curl http://localhost:8000/api/donors/1/stats
```

### Create an Event
```bash
curl -X POST http://localhost:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Annual Gala",
    "event_type": "gala",
    "start_date": "2024-06-15T18:00:00",
    "fundraising_goal": 100000,
    "capacity": 200
  }'
```

### Register Someone for Event
```bash
curl -X POST http://localhost:8000/api/events/1/registrations \
  -H "Content-Type: application/json" \
  -d '{
    "donor_id": 1,
    "number_of_guests": 2,
    "amount_paid": 500
  }'
```

### Log a Communication
```bash
curl -X POST http://localhost:8000/api/communications/ \
  -H "Content-Type: application/json" \
  -d '{
    "donor_id": 1,
    "communication_type": "email",
    "subject": "Thank you for your donation",
    "content": "Dear Jane, thank you for your generous support..."
  }'
```

### Run a Report
```bash
# Overview stats
curl http://localhost:8000/api/reports/stats/overview

# Execute a saved report
curl -X POST http://localhost:8000/api/reports/1/execute
```

---

## 4. API Quick Reference

### Base URL
```
http://localhost:8000/api/
```

### Authentication
Currently session-based (admin login). Token auth coming soon.

### Key Endpoints

| Resource | List | Create | Get | Update | Delete |
|----------|------|--------|-----|--------|--------|
| Donors | GET /donors | POST /donors | GET /donors/{id} | PUT /donors/{id} | DELETE /donors/{id} |
| Donations | GET /donations | POST /donations | GET /donations/{id} | PUT /donations/{id} | - |
| Campaigns | GET /campaigns | POST /campaigns | GET /campaigns/{id} | - | - |
| Events | GET /events | POST /events | GET /events/{id} | PUT /events/{id} | DELETE /events/{id} |
| Communications | GET /communications | POST /communications | GET /communications/{id} | PUT /communications/{id} | - |
| Reports | GET /reports | POST /reports | GET /reports/{id} | PUT /reports/{id} | DELETE /reports/{id} |

### Special Endpoints
- `GET /api/` - API root with all endpoints
- `GET /api/health` - Health check
- `GET /api/events/upcoming` - Upcoming events
- `GET /api/communications/followups` - Pending follow-ups
- `GET /api/reports/stats/overview` - Dashboard stats

---

## 5. Admin Interface

The Django Admin provides a web UI for all data:

**URL:** http://localhost:8000/admin/

**Features:**
- View/edit all donors, donations, campaigns
- Manage events and registrations
- Track communications
- Run and schedule reports
- User management

---

## 6. Development Mode

For local development with auto-reload:

```bash
# Stop production containers
docker compose down

# Start dev mode
docker compose -f compose.dev.yml up

# Or run directly
python manage.py runserver
```

---

## 7. Common Commands

```bash
# View logs
docker compose logs -f web

# Database shell
docker compose exec web python manage.py dbshell

# Django shell
docker compose exec web python manage.py shell

# Make migrations
docker compose exec web python manage.py makemigrations

# Run tests
docker compose exec web python manage.py test

# Backup database
docker compose exec db pg_dump -U crmuser fundraising_crm > backup.sql

# Stop everything
docker compose down

# Reset everything (WARNING: deletes data)
docker compose down -v
```

---

## 8. Next Steps

1. **Read the API docs** at `/api/docs` (when DEBUG=true)
2. **Explore the Admin** at `/admin/`
3. **Check DEPLOYMENT.md** for production setup
4. **Read END_USER_MANUAL.md** for detailed feature guide

---

## Troubleshooting

### Port already in use
```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Database locked
```bash
docker compose down
docker compose up -d
```

### Migration errors
```bash
docker compose exec web python manage.py migrate --run-syncdb
```

---

**You're ready to start fundraising!** 🎉
