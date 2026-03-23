# Django Fundraising CRM

A comprehensive fundraising CRM built with Django and Django-Ninja for REST API support. Manage donors, donations, campaigns, events, communications, and generate detailed reports.

## Features

- **Donor Management**: Track donor profiles, contact info, preferences, and giving history
- **Donation Tracking**: Record one-time and recurring donations with full audit trail
- **Campaign Management**: Create fundraising campaigns with goals and progress tracking
- **Event Management**: Plan galas, dinners, auctions with RSVP and sponsorship tracking
- **Communications**: Log all donor touchpoints (email, phone, SMS, meetings)
- **Reporting**: Built-in reports for donor analytics, LTV analysis, retention metrics
- **CLI Interface**: Full command-line management with table/JSON/CSV output
- **REST API**: Complete API with django-ninja for integrations

## Quick Start

### Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/intrepid-g/django-fundraising-crm.git
cd django-fundraising-crm

# Copy environment file
cp .env.example .env

# Start with Docker Compose
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## CLI Usage

The CRM includes a comprehensive CLI for all operations:

```bash
# List all donors
python cli.py donor list

# Search donors
python cli.py donor search "john"

# Get donor statistics
python cli.py donor stats

# List donations
python cli.py donation list

# View campaigns
python cli.py campaign list

# Generate reports
python cli.py report list
python cli.py report run donor-summary

# Output as JSON
python cli.py donor list --format json

# Output as CSV
python cli.py donor list --format csv
```

## API Endpoints

All data is accessible via REST API:

| Endpoint | Description |
|----------|-------------|
| `/api/donors/` | Donor CRUD + search + stats |
| `/api/donations/` | Donation CRUD + recurring + summary |
| `/api/campaigns/` | Campaign CRUD + stats |
| `/api/events/` | Events + registrations + sponsors |
| `/api/communications/` | Communications + templates + followups |
| `/api/reports/` | Reports + dashboards + metrics |

## Project Structure

```
django-fundraising-crm/
├── donors/          # Donor management
├── donations/       # Donation tracking
├── campaigns/       # Campaign management
├── events/          # Event planning
├── communications/  # Donor communications
├── reports/         # Analytics & reporting
├── fundraising_crm/ # Project settings
├── docs/            # Documentation
├── cli.py           # Command-line interface
└── manage.py        # Django management
```

## Documentation

- [Quick Start Guide](docs/QUICKSTART.md) - Get running in 5 minutes
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment
- [End User Manual](docs/END_USER_MANUAL.md) - Using the CRM
- [API Documentation](docs/API.md) - REST API reference
- [Changes Summary](CHANGES_SUMMARY.md) - Recent updates

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific app tests
pytest donors/tests.py
```

## Tech Stack

- **Backend**: Django 5.x
- **API**: Django-Ninja (FastAPI-style for Django)
- **Database**: PostgreSQL (production), SQLite (dev)
- **CLI**: argparse with rich table output
- **Testing**: pytest with django fixtures
- **Container**: Docker + Docker Compose

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details.

## Support

For issues and feature requests, please use the GitHub issue tracker.
