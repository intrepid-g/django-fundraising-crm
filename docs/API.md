# Django Fundraising CRM - API Documentation

Complete REST API reference for the Django Fundraising CRM.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

The API uses Django session authentication by default. For production, configure token-based authentication.

## Content-Type

All requests should include:
```
Content-Type: application/json
```

---

## Donors API

### List All Donors
```http
GET /api/donors/
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane@example.com",
      "phone": "+1-555-0123",
      "donor_type": "individual",
      "total_donations": "1500.00",
      "donation_count": 3,
      "email_opt_in": true,
      "created_at": "2026-01-15T10:30:00Z"
    }
  ],
  "count": 1
}
```

### Get Single Donor
```http
GET /api/donors/{id}/
```

### Create Donor
```http
POST /api/donors/
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1-555-0199",
  "donor_type": "individual",
  "address_line1": "123 Main St",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "US",
  "tags": ["major-donor", "newsletter"],
  "email_opt_in": true
}
```

### Update Donor
```http
PUT /api/donors/{id}/
PATCH /api/donors/{id}/
```

### Delete Donor
```http
DELETE /api/donors/{id}/
```

### Search Donors
```http
GET /api/donors/search/?q=john
```

### Get Donor Statistics
```http
GET /api/donors/stats/
```

---

## Donations API

### List All Donations
```http
GET /api/donations/
```

**Query Parameters:**
- `donor_id` - Filter by donor
- `campaign_id` - Filter by campaign
- `status` - Filter by status (pending, completed, failed, refunded)
- `start_date` - Filter from date (YYYY-MM-DD)
- `end_date` - Filter to date (YYYY-MM-DD)

### Get Single Donation
```http
GET /api/donations/{id}/
```

### Create Donation
```http
POST /api/donations/
```

**Request Body:**
```json
{
  "donor_id": 1,
  "amount": "250.00",
  "donation_type": "one-time",
  "payment_method": "credit-card",
  "campaign_id": 2,
  "is_tax_deductible": true,
  "notes": "Monthly giving campaign"
}
```

### Get Recurring Donations
```http
GET /api/donations/recurring/
```

### Get Donation Summary
```http
GET /api/donations/summary/
```

**Response:**
```json
{
  "total_amount": "50000.00",
  "total_count": 150,
  "average_amount": "333.33",
  "by_type": {
    "one-time": "35000.00",
    "recurring": "15000.00"
  }
}
```

---

## Campaigns API

### List All Campaigns
```http
GET /api/campaigns/
```

### Get Single Campaign
```http
GET /api/campaigns/{id}/
```

### Create Campaign
```http
POST /api/campaigns/
```

**Request Body:**
```json
{
  "name": "Spring Fundraiser 2026",
  "description": "Annual spring fundraising campaign",
  "goal_amount": "100000.00",
  "start_date": "2026-03-01",
  "end_date": "2026-05-31",
  "is_active": true
}
```

### Get Campaign Statistics
```http
GET /api/campaigns/{id}/stats/
```

**Response:**
```json
{
  "total_raised": "75000.00",
  "progress_percentage": 75.0,
  "donor_count": 45,
  "days_remaining": 30
}
```

---

## Events API

### List All Events
```http
GET /api/events/
```

**Query Parameters:**
- `status` - Filter by status (draft, planning, open, closed, completed, cancelled)
- `event_type` - Filter by type (gala, dinner, auction, meeting, webinar, other)
- `upcoming` - Set to `true` for future events only

### Get Single Event
```http
GET /api/events/{id}/
```

### Create Event
```http
POST /api/events/
```

**Request Body:**
```json
{
  "name": "Annual Charity Gala",
  "description": "Our biggest fundraising event of the year",
  "event_type": "gala",
  "status": "planning",
  "start_date": "2026-06-15T18:00:00Z",
  "end_date": "2026-06-15T23:00:00Z",
  "venue_name": "Grand Ballroom",
  "venue_address": "123 Park Avenue",
  "venue_city": "New York",
  "capacity": 200,
  "fundraising_goal": 50000,
  "ticket_price": 250
}
```

### Event Registrations

#### List Registrations
```http
GET /api/events/{id}/registrations/
```

#### Register Attendee
```http
POST /api/events/{id}/registrations/
```

**Request Body:**
```json
{
  "donor_id": 1,
  "guests_count": 2,
  "dietary_restrictions": "Vegetarian",
  "special_requests": "Near the stage please"
}
```

#### Check In Attendee
```http
POST /api/events/{id}/registrations/{registration_id}/check-in/
```

### Event Sponsors

#### List Sponsors
```http
GET /api/events/{id}/sponsors/
```

#### Add Sponsor
```http
POST /api/events/{id}/sponsors/
```

**Request Body:**
```json
{
  "donor_id": 1,
  "sponsorship_level": "platinum",
  "amount": 10000,
  "benefits": "Logo on all materials, 10 tickets, VIP table"
}
```

### Event Tasks

#### List Tasks
```http
GET /api/events/{id}/tasks/
```

#### Create Task
```http
POST /api/events/{id}/tasks/
```

**Request Body:**
```json
{
  "title": "Book catering",
  "description": "Contact caterers and get quotes",
  "assigned_to": "events@organization.org",
  "due_date": "2026-05-15",
  "priority": "high"
}
```

### Get Event Statistics
```http
GET /api/events/stats/
```

---

## Communications API

### List All Communications
```http
GET /api/communications/
```

### Get Single Communication
```http
GET /api/communications/{id}/
```

### Create Communication
```http
POST /api/communications/
```

**Request Body:**
```json
{
  "donor_id": 1,
  "communication_type": "email",
  "subject": "Thank you for your donation",
  "content": "Dear John, thank you for your generous support...",
  "sent_at": "2026-03-15T10:00:00Z"
}
```

### Communication Templates

#### List Templates
```http
GET /api/communications/templates/
```

#### Create Template
```http
POST /api/communications/templates/
```

**Request Body:**
```json
{
  "name": "Thank You Email",
  "template_type": "email",
  "subject": "Thank you, {{ donor.first_name }}!",
  "content": "Dear {{ donor.first_name }}, thank you for your {{ donation.amount }} donation..."
}
```

#### Render Template
```http
POST /api/communications/templates/{id}/render/
```

**Request Body:**
```json
{
  "donor_id": 1,
  "donation_id": 5
}
```

### Scheduled Communications

#### List Scheduled
```http
GET /api/communications/scheduled/
```

#### Schedule Communication
```http
POST /api/communications/scheduled/
```

**Request Body:**
```json
{
  "template_id": 1,
  "donor_id": 1,
  "scheduled_for": "2026-04-01T09:00:00Z",
  "frequency": "monthly"
}
```

### Follow-ups
```http
GET /api/communications/follow-ups/
```

---

## Reports API

### List All Reports
```http
GET /api/reports/
```

### Get Single Report
```http
GET /api/reports/{id}/
```

### Create Report
```http
POST /api/reports/
```

**Request Body:**
```json
{
  "name": "Monthly Donation Summary",
  "report_type": "donation_summary",
  "description": "Summary of all donations for the month",
  "configuration": {
    "date_range": "last_30_days",
    "group_by": "campaign"
  }
}
```

### Execute Report
```http
POST /api/reports/{id}/execute/
```

**Response:**
```json
{
  "execution_id": 15,
  "status": "completed",
  "results": {
    "total_amount": "25000.00",
    "donation_count": 45,
    "by_campaign": [...]
  },
  "generated_at": "2026-03-28T07:30:00Z"
}
```

### Dashboards

#### List Dashboards
```http
GET /api/reports/dashboards/
```

#### Create Dashboard
```http
POST /api/reports/dashboards/
```

### Quick Overview
```http
GET /api/reports/overview/
```

**Response:**
```json
{
  "total_donors": 150,
  "total_donations": "500000.00",
  "active_campaigns": 3,
  "upcoming_events": 2,
  "recent_donations": [...],
  "top_donors": [...]
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data",
  "errors": {
    "email": ["Enter a valid email address."]
  }
}
```

### 404 Not Found
```json
{
  "detail": "Not found"
}
```

### 500 Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Default rate limits:
- 100 requests per minute for authenticated users
- 20 requests per minute for anonymous users

---

## Pagination

List endpoints support pagination:

```http
GET /api/donors/?limit=10&offset=20
```

**Response:**
```json
{
  "items": [...],
  "count": 100,
  "next": "/api/donors/?limit=10&offset=30",
  "previous": "/api/donors/?limit=10&offset=10"
}
```

---

## Filtering & Sorting

### Filter Examples
```http
GET /api/donors/?donor_type=individual
GET /api/donations/?status=completed&start_date=2026-01-01
GET /api/events/?status=upcoming
```

### Sort Examples
```http
GET /api/donors/?sort=-total_donations
GET /api/donations/?sort=-donation_date
```

---

## Webhooks (Planned)

Future versions will support webhooks for:
- New donations
- Donor updates
- Campaign milestones
- Event registrations

---

## SDK & Client Libraries

Official client libraries (planned):
- Python: `pip install django-crm-client`
- JavaScript/Node: `npm install django-crm-client`
- PHP: `composer require django-crm/client`

---

## Changelog

### v1.0.0 (2026-03-28)
- Initial API release
- Full CRUD for donors, donations, campaigns
- Event management with registrations and sponsors
- Communications with templates
- Reporting and dashboards

---

## Support

For API support:
- GitHub Issues: https://github.com/intrepid-g/django-fundraising-crm/issues
- Documentation: https://github.com/intrepid-g/django-fundraising-crm/tree/main/docs
