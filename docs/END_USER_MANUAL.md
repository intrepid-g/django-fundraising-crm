# Django Fundraising CRM - End User Manual

Complete guide for using the Fundraising CRM system.

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Donor Management](#donor-management)
4. [Donation Tracking](#donation-tracking)
5. [Campaign Management](#campaign-management)
6. [Event Management](#event-management)
7. [Communications](#communications)
8. [Reports & Analytics](#reports--analytics)
9. [Dashboards](#dashboards)
10. [Best Practices](#best-practices)

---

## Introduction

The Django Fundraising CRM is a comprehensive donor management system designed for non-profits, charities, and fundraising organizations. It helps you:

- **Track donors** and their giving history
- **Manage donations** (one-time, recurring, in-kind)
- **Run campaigns** with goals and progress tracking
- **Organize events** (galas, dinners, auctions)
- **Log communications** with donors
- **Generate reports** and analytics

---

## Getting Started

### Login
1. Navigate to your CRM URL (e.g., `https://crm.yourorg.com`)
2. Click "Admin" or go to `/admin/`
3. Enter your username and password

### Navigation
The main sections are accessible from the admin sidebar:
- **Donors** - All donor records
- **Donations** - Donation history
- **Campaigns** - Fundraising campaigns
- **Events** - Event management
- **Communications** - Donor interactions
- **Reports** - Analytics and dashboards

---

## Donor Management

### Creating a Donor

**Via Admin:**
1. Go to Donors → Add Donor
2. Fill in required fields:
   - First Name
   - Last Name
   - Email (unique identifier)
3. Optional fields:
   - Phone, Address
   - Donor Type (Individual/Organization/Foundation)
   - Organization Name (if applicable)
   - Tags for segmentation

**Via API:**
```bash
curl -X POST /api/donors/ -d '{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "donor_type": "individual",
  "tags": ["major_donor", "board_member"]
}'
```

### Donor Types
- **Individual** - Single person donor
- **Organization** - Company or group
- **Foundation** - Grant-making foundation

### Tags & Segmentation
Use tags to categorize donors:
- `major_donor` - High-value donors
- `recurring_donor` - Monthly/annual donors
- `board_member` - Board connections
- `volunteer` - Also volunteers
- `lapsed` - No recent donations
- `prospect` - Potential donors

### Viewing Donor History
1. Click on any donor
2. View tabs:
   - **Donations** - All giving history
   - **Communications** - All interactions
   - **Event Registrations** - Event attendance
   - **Stats** - Summary metrics

### Donor Statistics
Each donor automatically tracks:
- Total donations (lifetime)
- Donation count
- First donation date
- Last donation date
- Average donation amount

---

## Donation Tracking

### Recording a Donation

**Via Admin:**
1. Go to Donations → Add Donation
2. Select donor
3. Enter amount
4. Choose donation type:
   - **One-time** - Single gift
   - **Recurring** - Monthly/annual subscription
   - **In-kind** - Goods/services
   - **Matching** - Corporate match
   - **Stock** - Securities donation
   - **Legacy** - Planned/bequest gift

### Donation Status
- **Pending** - Not yet received
- **Completed** - Successfully processed
- **Failed** - Payment failed
- **Refunded** - Returned to donor
- **Cancelled** - Recurring cancelled

### Recurring Donations
Set up automatic recurring gifts:
1. Create donation with `donation_type: recurring`
2. Set `recurring_frequency`: monthly, quarterly, or annual
3. System tracks `recurring_status`: active, paused, cancelled

### Campaign Attribution
Link donations to campaigns:
1. Select campaign from dropdown
2. Donation counts toward campaign goal
3. View campaign progress in real-time

### Acknowledgments
Track thank-you notes:
- `acknowledgment_sent` - Boolean
- `acknowledgment_date` - When sent
- `acknowledgment_method` - Email, mail, phone

---

## Campaign Management

### Creating a Campaign

**Required fields:**
- Name (e.g., "Spring 2024 Fundraiser")
- Goal Amount (e.g., $50,000)
- Start Date

**Optional:**
- End Date
- Description
- Is Active toggle

### Campaign Goals
Set realistic fundraising goals:
- Consider past performance
- Factor in donor capacity
- Break into milestones

### Tracking Progress
Campaigns automatically calculate:
- Total raised
- Percentage of goal
- Number of donors
- Average donation
- Days remaining

### Campaign Events
Link events to campaigns:
1. Create event
2. Select campaign in "Campaign" field
3. Event fundraising counts toward goal

---

## Event Management

### Event Types
- **Gala** - Formal fundraising dinner
- **Dinner** - Casual meal event
- **Auction** - Silent or live auction
- **Golf Tournament** - Sporting fundraiser
- **Walkathon** - Peer-to-peer event
- **Concert** - Performance fundraiser
- **Meeting** - Board/staff meeting

### Creating an Event

**Via Admin:**
1. Events → Add Event
2. Fill details:
   - Name, Type, Status
   - Date/Time (start, end, setup)
   - Venue information
   - Capacity
   - Fundraising goals

### Event Status Workflow
1. **Draft** - Planning phase
2. **Planning** - Active preparation
3. **Confirmed** - Ready to promote
4. **In Progress** - Event happening
5. **Completed** - Finished
6. **Cancelled** - Not happening

### Registrations
Track RSVPs:
1. Go to event → Registrations
2. Add registration:
   - Select donor
   - Number of guests
   - Dietary requirements
   - Amount paid (if ticketed)

### Check-in
At event, check in attendees:
1. Go to event → Registrations
2. Click "Check In" on each attendee
3. Or use API: `POST /api/events/{id}/registrations/{id}/checkin`

### Event Sponsors
Track sponsorships:
- Sponsor name/level (Platinum/Gold/Silver/Bronze)
- Amount pledged
- Benefits provided
- Status (pending/confirmed/paid)

### Event Tasks
Manage to-do lists:
- Create tasks with due dates
- Assign to staff
- Track completion
- Set priorities (high/medium/low)

---

## Communications

### Types of Communications
- **Email** - Electronic messages
- **Phone Call** - Voice conversations
- **Meeting** - In-person meetings
- **Note** - Internal notes
- **Letter** - Physical mail
- **SMS** - Text messages
- **Social Media** - Social interactions

### Logging a Communication

**Via Admin:**
1. Communications → Add Communication
2. Select donor
3. Choose type and direction (inbound/outbound)
4. Enter subject and content
5. Add summary for quick reference

### Follow-ups
Mark communications needing follow-up:
1. Check "Requires Follow-up"
2. Set follow-up date
3. View all pending: Communications → Follow-ups
4. Mark complete when done

### Communication Templates
Create reusable templates:
1. Communications → Templates → Add
2. Enter:
   - Name (e.g., "Thank You Email")
   - Type (email/SMS/letter)
   - Subject template
   - Body template
3. Use variables: `{{ donor.first_name }}`, `{{ donation.amount }}`

### Scheduled Communications
Automate outreach:
1. Create schedule:
   - Select donor
   - Choose template or write custom
   - Set date/time
2. System sends automatically
3. View status in Scheduled Communications

### Communication Preferences
Respect donor preferences:
1. Go to donor → Preferences
2. Set:
   - Email/phone/SMS/mail opt-ins
   - Preferred frequency
   - Contact time
   - Topics of interest
3. System respects "Do Not Contact" flags

---

## Reports & Analytics

### Built-in Reports

#### 1. Donor Analytics
- Total donors, new donors, active donors
- Donors by type
- Top donors by lifetime value
- Lapsed donor identification

#### 2. Donation Summary
- Total raised, count, average
- By donation type
- Monthly trends
- Year-over-year comparison

#### 3. Campaign Performance
- Goal progress
- ROI by campaign
- Donor acquisition
- Conversion rates

#### 4. LTV Analysis
Segments donors by lifetime value:
- **Champions** - $10,000+
- **Loyal** - $1,000-$9,999
- **Potential** - $100-$999
- **New** - $1-$99

#### 5. Retention Analysis
- Retention rate (donors who gave again)
- Churned donors
- Reactivation opportunities

### Running Reports

**Via Admin:**
1. Reports → Add Report
2. Select report type
3. Configure:
   - Date range (preset or custom)
   - Filters (donor type, tags, etc.)
   - Grouping options
4. Save for reuse or run once

**Via API:**
```bash
# Execute report
curl -X POST /api/reports/{id}/execute

# Get overview stats
curl /api/reports/stats/overview
```

### Scheduled Reports
Automate report delivery:
1. Edit report → Scheduling
2. Enable "Is Scheduled"
3. Set frequency (daily/weekly/monthly)
4. Add email recipients
5. System emails PDF/Excel automatically

---

## Dashboards

### Default Dashboard
Overview of key metrics:
- Total donors
- Donations this month
- Active campaigns
- Upcoming events
- Pending follow-ups

### Custom Dashboards
Create role-specific views:
1. Reports → Dashboards → Add
2. Name your dashboard
3. Add widgets:
   - Metric cards (single numbers)
   - Charts (bar, line, pie)
   - Lists (recent donations, upcoming events)
4. Arrange layout
5. Set as default if desired

### Widget Types
- **Metric** - Single number with label
- **Chart** - Visual data representation
- **List** - Scrollable record list
- **Table** - Data table with columns

### Sharing Dashboards
- **Private** - Only you
- **Shared** - All staff can view
- **Default** - New users see this

---

## Best Practices

### Data Entry
1. **Be consistent** - Use standard naming
2. **Enter promptly** - Log donations same day
3. **Be thorough** - Fill all relevant fields
4. **Use tags** - Enable segmentation
5. **Log communications** - Complete interaction history

### Donor Relations
1. **Thank within 48 hours** - Acknowledge quickly
2. **Personalize** - Use donor preferences
3. **Track interactions** - Log all touchpoints
4. **Follow up** - Complete promised actions
5. **Respect opt-outs** - Honor communication preferences

### Campaign Planning
1. **Set realistic goals** - Based on past performance
2. **Create timeline** - Start planning early
3. **Track expenses** - Monitor ROI
4. **Segment appeals** - Target by donor type
5. **Report progress** - Share with stakeholders

### Event Management
1. **Plan early** - 3-6 months for major events
2. **Track all costs** - Venue, catering, marketing
3. **Manage capacity** - Don't oversell tickets
4. **Follow up** - Thank attendees promptly
5. **Analyze results** - What worked/didn't

### Reporting
1. **Review monthly** - Regular performance checks
2. **Share with board** - Quarterly reports
3. **Track trends** - Year-over-year comparisons
4. **Identify opportunities** - Lapsed donors, major gifts
5. **Celebrate wins** - Share successes with team

### Security
1. **Strong passwords** - Use password manager
2. **Log out** - When leaving workstation
3. **Don't share accounts** - Individual logins
4. **Report issues** - Suspicious activity immediately
5. **Backup awareness** - Know recovery procedures

---

## Keyboard Shortcuts

### Admin Interface
- `Ctrl + S` - Save form
- `Ctrl + F` - Search page
- `?` - Show keyboard shortcuts

### API Testing
Use tools like:
- Postman
- Insomnia
- curl (command line)
- HTTPie

---

## Getting Help

### In-App Help
- Hover over field labels for descriptions
- Click "?" icons for detailed help

### Documentation
- API docs: `/api/docs` (development mode)
- This manual
- Deployment guide
- Quick start guide

### Support
- GitHub Issues: https://github.com/intrepid-g/django-fundraising-crm/issues
- Email: support@yourorg.com
- Slack/Teams: #fundraising-crm channel

---

## Glossary

| Term | Definition |
|------|------------|
| **Campaign** | Fundraising initiative with specific goal and timeframe |
| **Donor** | Individual or organization that gives money |
| **Donation** | Single gift transaction |
| **Recurring** | Automatic repeating donation |
| **LTV** | Lifetime Value - total given by donor |
| **Retention** | Rate of donors who give again |
| **Churn** | Donors who stop giving |
| **Segment** | Group of donors with shared characteristics |
| **Acknowledgment** | Thank-you note for donation |
| **Pledge** | Promise to give in future |

---

**Happy Fundraising!** 🎉
