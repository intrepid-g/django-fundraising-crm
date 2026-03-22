#!/usr/bin/env python3
"""
Django Fundraising CRM - CLI Interface

A command-line interface for managing donors, donations, campaigns, events, and reports.

Setup:
    pip install django django-ninja

Usage:
    python cli.py donor list
    python cli.py donor get <id>
    python cli.py donor create --first-name John --last-name Doe --email john@example.com
    python cli.py donation create --donor-id <id> --amount 100.00 --campaign-id <id>
    python cli.py campaign list
    python cli.py event list
    python cli.py report run donor-summary
"""

import argparse
import json
import sys
import os
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Optional

# Django setup - only when commands are actually run
def setup_django():
    """Setup Django environment."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fundraising_crm.settings')
    import django
    django.setup()


class CustomJSONEncoder(json.JSONEncoder):
    """Handle Decimal and date serialization."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def format_output(data: Any, format_type: str = 'table') -> str:
    """Format output as table, json, or csv."""
    if format_type == 'json':
        return json.dumps(data, cls=CustomJSONEncoder, indent=2)
    
    if format_type == 'csv':
        if not data:
            return "No data"
        if isinstance(data, list) and len(data) > 0:
            headers = list(data[0].keys())
            lines = ['"' + '","'.join(headers) + '"']
            for row in data:
                values = [str(row.get(h, '')).replace('"', '""') for h in headers]
                lines.append('"' + '","'.join(values) + '"')
            return '\n'.join(lines)
        return str(data)
    
    # Table format (default)
    if not data:
        return "No data found."
    
    if isinstance(data, dict):
        lines = []
        for key, value in data.items():
            lines.append(f"{key:20s}: {value}")
        return '\n'.join(lines)
    
    if isinstance(data, list):
        if not data:
            return "No items found."
        # Get all unique keys
        keys = set()
        for item in data:
            if isinstance(item, dict):
                keys.update(item.keys())
        keys = sorted(keys)
        
        if not keys:
            return '\n'.join(str(item) for item in data)
        
        # Calculate column widths
        widths = {key: len(key) for key in keys}
        for item in data:
            for key in keys:
                val_str = str(item.get(key, ''))[:50]
                widths[key] = max(widths[key], len(val_str))
        
        # Build table
        lines = []
        header = ' | '.join(key[:widths[key]].ljust(widths[key]) for key in keys)
        lines.append(header)
        lines.append('-' * len(header))
        
        for item in data:
            row = ' | '.join(
                str(item.get(key, ''))[:50].ljust(widths[key]) 
                for key in keys
            )
            lines.append(row)
        
        return '\n'.join(lines)
    
    return str(data)


# ============== DONOR COMMANDS ==============

def donor_list(args):
    """List all donors."""
    setup_django()
    from donors.models import Donor
    
    donors = Donor.objects.all()
    if args.limit:
        donors = donors[:args.limit]
    
    data = []
    for d in donors:
        data.append({
            'id': str(d.id),
            'name': f"{d.first_name} {d.last_name}",
            'email': d.email,
            'type': d.donor_type,
            'total_donations': d.total_donations,
            'donation_count': d.donation_count,
            'active': 'Yes' if d.email_opt_in else 'No'
        })
    
    print(format_output(data, args.format))
    print(f"\nTotal: {len(data)} donors")


def donor_get(args):
    """Get a specific donor by ID or email."""
    setup_django()
    from donors.models import Donor
    
    try:
        if args.id:
            donor = Donor.objects.get(id=args.id)
        elif args.email:
            donor = Donor.objects.get(email=args.email)
        else:
            print("Error: Provide --id or --email")
            return
        
        data = {
            'id': str(donor.id),
            'first_name': donor.first_name,
            'last_name': donor.last_name,
            'email': donor.email,
            'phone': donor.phone,
            'donor_type': donor.donor_type,
            'organization_name': donor.organization_name,
            'address': f"{donor.address_line1}, {donor.city}, {donor.state} {donor.postal_code}",
            'tags': ', '.join(donor.tags) if donor.tags else 'None',
            'segments': ', '.join(donor.segments) if donor.segments else 'None',
            'total_donations': donor.total_donations,
            'donation_count': donor.donation_count,
            'first_donation': donor.first_donation_date,
            'last_donation': donor.last_donation_date,
            'email_opt_in': donor.email_opt_in,
            'created_at': donor.created_at,
            'updated_at': donor.updated_at,
        }
        print(format_output(data, args.format))
        
    except Donor.DoesNotExist:
        print(f"Error: Donor not found")


def donor_create(args):
    """Create a new donor."""
    setup_django()
    from donors.models import Donor
    
    donor = Donor.objects.create(
        first_name=args.first_name,
        last_name=args.last_name,
        email=args.email,
        phone=args.phone or '',
        donor_type=args.type or 'individual',
        organization_name=args.organization or '',
        address_line1=args.address or '',
        city=args.city or '',
        state=args.state or '',
        postal_code=args.postal or '',
        tags=args.tags.split(',') if args.tags else [],
    )
    print(f"Created donor: {donor.first_name} {donor.last_name} (ID: {donor.id})")


def donor_search(args):
    """Search donors by name or email."""
    setup_django()
    from donors.models import Donor
    from django.db.models import Q
    
    query = args.query
    donors = Donor.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query) |
        Q(organization_name__icontains=query)
    )
    
    if args.limit:
        donors = donors[:args.limit]
    
    data = []
    for d in donors:
        data.append({
            'id': str(d.id),
            'name': f"{d.first_name} {d.last_name}",
            'email': d.email,
            'type': d.donor_type,
            'total_donations': d.total_donations,
        })
    
    print(format_output(data, args.format))
    print(f"\nFound: {len(data)} donors")


def donor_update(args):
    """Update a donor."""
    setup_django()
    from donors.models import Donor
    
    try:
        donor = Donor.objects.get(id=args.id)
        
        if args.first_name:
            donor.first_name = args.first_name
        if args.last_name:
            donor.last_name = args.last_name
        if args.email:
            donor.email = args.email
        if args.phone:
            donor.phone = args.phone
        if args.tags:
            donor.tags = args.tags.split(',')
        
        donor.save()
        print(f"Updated donor: {donor.first_name} {donor.last_name}")
        
    except Donor.DoesNotExist:
        print(f"Error: Donor not found")


def donor_delete(args):
    """Delete a donor."""
    setup_django()
    from donors.models import Donor
    
    try:
        donor = Donor.objects.get(id=args.id)
        name = f"{donor.first_name} {donor.last_name}"
        donor.delete()
        print(f"Deleted donor: {name}")
    except Donor.DoesNotExist:
        print(f"Error: Donor not found")


def donor_stats(args):
    """Show donor statistics."""
    setup_django()
    from donors.models import Donor
    from django.db.models import Count, Sum, Avg
    
    stats = Donor.objects.aggregate(
        total=Count('id'),
        with_donations=Count('id', filter=models.Q(donation_count__gt=0)),
        total_donated=Sum('total_donations'),
        avg_donation=Avg('total_donations')
    )
    
    by_type = Donor.objects.values('donor_type').annotate(
        count=Count('id'),
        total=Sum('total_donations')
    )
    
    print("=== Donor Statistics ===")
    print(f"Total donors: {stats['total']}")
    print(f"Donors with donations: {stats['with_donations']}")
    print(f"Total donated: ${stats['total_donated'] or 0:,.2f}")
    print(f"Avg per donor: ${stats['avg_donation'] or 0:,.2f}")
    print("\nBy type:")
    for t in by_type:
        print(f"  {t['donor_type']}: {t['count']} (${t['total'] or 0:,.2f})")


# ============== DONATION COMMANDS ==============

def donation_list(args):
    """List donations."""
    setup_django()
    from donations.models import Donation, Campaign
    from donors.models import Donor
    
    donations = Donation.objects.all().select_related('donor', 'campaign')
    if args.donor_id:
        donations = donations.filter(donor_id=args.donor_id)
    if args.campaign_id:
        donations = donations.filter(campaign_id=args.campaign_id)
    if args.limit:
        donations = donations[:args.limit]
    
    data = []
    for d in donations:
        data.append({
            'id': str(d.id),
            'donor': f"{d.donor.first_name} {d.donor.last_name}",
            'amount': d.amount,
            'campaign': d.campaign.name if d.campaign else 'None',
            'date': d.donation_date,
            'status': d.status,
            'method': d.payment_method,
        })
    
    print(format_output(data, args.format))
    print(f"\nTotal: {len(data)} donations")


def donation_create(args):
    """Create a donation."""
    setup_django()
    from donations.models import Donation, Campaign
    from donors.models import Donor
    
    try:
        donor = Donor.objects.get(id=args.donor_id)
        
        campaign = None
        if args.campaign_id:
            campaign = Campaign.objects.get(id=args.campaign_id)
        
        donation = Donation.objects.create(
            donor=donor,
            campaign=campaign,
            amount=args.amount,
            payment_method=args.method or 'credit_card',
            donation_date=args.date or date.today(),
            status='completed' if args.completed else 'pending',
        )
        
        print(f"Created donation: ${donation.amount} from {donor.first_name} {donor.last_name}")
        
    except Donor.DoesNotExist:
        print("Error: Donor not found")
    except Campaign.DoesNotExist:
        print("Error: Campaign not found")


def donation_summary(args):
    """Show donation summary."""
    setup_django()
    from donations.models import Donation
    from django.db.models import Sum, Count, Avg
    from django.utils import timezone
    
    today = timezone.now().date()
    
    # Overall stats
    stats = Donation.objects.aggregate(
        total=Sum('amount'),
        count=Count('id'),
        avg=Avg('amount')
    )
    
    # This month
    this_month = Donation.objects.filter(
        donation_date__year=today.year,
        donation_date__month=today.month
    ).aggregate(total=Sum('amount'), count=Count('id'))
    
    # By status
    by_status = Donation.objects.values('status').annotate(
        total=Sum('amount'),
        count=Count('id')
    )
    
    print("=== Donation Summary ===")
    print(f"Total donations: {stats['count']} (${stats['total'] or 0:,.2f})")
    print(f"Average: ${stats['avg'] or 0:,.2f}")
    print(f"\nThis month: {this_month['count']} (${this_month['total'] or 0:,.2f})")
    print("\nBy status:")
    for s in by_status:
        print(f"  {s['status']}: {s['count']} (${s['total'] or 0:,.2f})")


# ============== CAMPAIGN COMMANDS ==============

def campaign_list(args):
    """List campaigns."""
    setup_django()
    from donations.models import Campaign
    
    campaigns = Campaign.objects.all()
    if args.active:
        campaigns = campaigns.filter(status='active')
    
    data = []
    for c in campaigns:
        data.append({
            'id': str(c.id),
            'name': c.name,
            'type': c.campaign_type,
            'status': c.status,
            'goal': c.goal_amount,
            'current': c.current_amount,
            'percent': f"{c.percent_funded:.1f}%",
            'start': c.start_date,
            'end': c.end_date,
        })
    
    print(format_output(data, args.format))
    print(f"\nTotal: {len(data)} campaigns")


def campaign_get(args):
    """Get campaign details."""
    setup_django()
    from donations.models import Campaign
    
    try:
        c = Campaign.objects.get(id=args.id)
        data = {
            'id': str(c.id),
            'name': c.name,
            'description': c.description,
            'type': c.campaign_type,
            'status': c.status,
            'goal_amount': c.goal_amount,
            'current_amount': c.current_amount,
            'percent_funded': f"{c.percent_funded:.1f}%",
            'start_date': c.start_date,
            'end_date': c.end_date,
            'is_tax_deductible': c.is_tax_deductible,
        }
        print(format_output(data, args.format))
    except Campaign.DoesNotExist:
        print("Error: Campaign not found")


def campaign_create(args):
    """Create a campaign."""
    setup_django()
    from donations.models import Campaign
    
    campaign = Campaign.objects.create(
        name=args.name,
        description=args.description or '',
        campaign_type=args.type or 'annual',
        goal_amount=args.goal,
        start_date=args.start_date or date.today(),
        end_date=args.end_date,
    )
    print(f"Created campaign: {campaign.name} (ID: {campaign.id})")


# ============== EVENT COMMANDS ==============

def event_list(args):
    """List events."""
    setup_django()
    from events.models import Event
    
    events = Event.objects.all()
    if args.upcoming:
        from django.utils import timezone
        events = events.filter(start_date__gte=timezone.now().date())
    
    data = []
    for e in events:
        data.append({
            'id': str(e.id),
            'name': e.name,
            'type': e.event_type,
            'start': e.start_date,
            'end': e.end_date,
            'location': e.location or 'Virtual',
            'capacity': e.capacity,
            'registered': e.registered_count,
        })
    
    print(format_output(data, args.format))
    print(f"\nTotal: {len(data)} events")


def event_get(args):
    """Get event details."""
    setup_django()
    from events.models import Event
    
    try:
        e = Event.objects.get(id=args.id)
        data = {
            'id': str(e.id),
            'name': e.name,
            'description': e.description,
            'type': e.event_type,
            'start_date': e.start_date,
            'end_date': e.end_date,
            'location': e.location,
            'capacity': e.capacity,
            'registered': e.registered_count,
            'checked_in': e.checked_in_count,
        }
        print(format_output(data, args.format))
    except Event.DoesNotExist:
        print("Error: Event not found")


# ============== REPORT COMMANDS ==============

def report_list(args):
    """List available reports."""
    reports = [
        {'id': 'donor-summary', 'name': 'Donor Summary', 'description': 'Overview of all donors'},
        {'id': 'donation-trends', 'name': 'Donation Trends', 'description': 'Monthly donation trends'},
        {'id': 'campaign-performance', 'name': 'Campaign Performance', 'description': 'Campaign progress and stats'},
        {'id': 'lapsed-donors', 'name': 'Lapsed Donors', 'description': 'Donors with no recent donations'},
        {'id': 'top-donors', 'name': 'Top Donors', 'description': 'Highest value donors'},
    ]
    print(format_output(reports, args.format))


def report_run(args):
    """Run a report."""
    setup_django()
    from donors.models import Donor
    from donations.models import Donation, Campaign
    from django.db.models import Sum, Count, Avg
    from django.utils import timezone
    from datetime import timedelta
    
    report_id = args.report_id
    
    if report_id == 'donor-summary':
        stats = Donor.objects.aggregate(
            total=Count('id'),
            with_donations=Count('id', filter=models.Q(donation_count__gt=0)),
            total_donated=Sum('total_donations'),
        )
        print("=== Donor Summary Report ===")
        print(f"Total donors: {stats['total']}")
        print(f"Active donors: {stats['with_donations']}")
        print(f"Total donated: ${stats['total_donated'] or 0:,.2f}")
    
    elif report_id == 'top-donors':
        top = Donor.objects.order_by('-total_donations')[:10]
        print("=== Top 10 Donors ===")
        for i, d in enumerate(top, 1):
            print(f"{i}. {d.first_name} {d.last_name}: ${d.total_donations:,.2f} ({d.donation_count} donations)")
    
    elif report_id == 'lapsed-donors':
        six_months_ago = timezone.now().date() - timedelta(days=180)
        lapsed = Donor.objects.filter(
            donation_count__gt=0,
            last_donation_date__lt=six_months_ago
        )
        print(f"=== Lapsed Donors (no donation in 6+ months) ===")
        print(f"Count: {lapsed.count()}")
        for d in lapsed[:20]:
            print(f"  - {d.first_name} {d.last_name} (last: {d.last_donation_date})")
    
    elif report_id == 'campaign-performance':
        campaigns = Campaign.objects.all()
        print("=== Campaign Performance ===")
        for c in campaigns:
            status = "✓" if c.percent_funded >= 100 else "○"
            print(f"{status} {c.name}: ${c.current_amount:,.2f} / ${c.goal_amount:,.2f} ({c.percent_funded:.1f}%)")
    
    else:
        print(f"Unknown report: {report_id}")


# ============== MAIN CLI ==============

def main():
    parser = argparse.ArgumentParser(
        description='Django Fundraising CRM CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s donor list --limit 10
  %(prog)s donor create --first-name John --last-name Doe --email john@example.com
  %(prog)s donation create --donor-id <uuid> --amount 100.00
  %(prog)s campaign list --active
  %(prog)s report run top-donors
        """
    )
    
    parser.add_argument('--format', choices=['table', 'json', 'csv'], default='table',
                        help='Output format')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Donor commands
    donor_parser = subparsers.add_parser('donor', help='Donor management')
    donor_subparsers = donor_parser.add_subparsers(dest='donor_action')
    
    # donor list
    donor_list_parser = donor_subparsers.add_parser('list', help='List donors')
    donor_list_parser.add_argument('--limit', type=int, help='Limit results')
    donor_list_parser.add_argument('--format', choices=['table', 'json', 'csv'], default='table')
    
    # donor get
    donor_get_parser = donor_subparsers.add_parser('get', help='Get donor details')
    donor_get_parser.add_argument('--id', help='Donor ID')
    donor_get_parser.add_argument('--email', help='Donor email')
    donor_get_parser.add_argument('--format', choices=['table', 'json', 'csv'], default='table')
    
    # donor create
    donor_create_parser = donor_subparsers.add_parser('create', help='Create donor')
    donor_create_parser.add_argument('--first-name', required=True)
    donor_create_parser.add_argument('--last-name', required=True)
    donor_create_parser.add_argument('--email', required=True)
    donor_create_parser.add_argument('--phone')
    donor_create_parser.add_argument('--type', choices=['individual', 'organization', 'foundation'])
    donor_create_parser.add_argument('--organization')
    donor_create_parser.add_argument('--address')
    donor_create_parser.add_argument('--city')
    donor_create_parser.add_argument('--state')
    donor_create_parser.add_argument('--postal')
    donor_create_parser.add_argument('--tags')
    
    # donor search
    donor_search_parser = donor_subparsers.add_parser('search', help='Search donors')
    donor_search_parser.add_argument('query', help='Search query')
    donor_search_parser.add_argument('--limit', type=int, default=20)
    donor_search_parser.add_argument('--format', choices=['table', 'json', 'csv'], default='table')
    
    # donor update
    donor_update_parser = donor_subparsers.add_parser('update', help='Update donor')
    donor_update_parser.add_argument('--id', required=True)
    donor_update_parser.add_argument('--first-name')
    donor_update_parser.add_argument('--last-name')
    donor_update_parser.add_argument('--email')
    donor_update_parser.add_argument('--phone')
    donor_update_parser.add_argument('--tags')
    
    # donor delete
    donor_delete_parser = donor_subparsers.add_parser('delete', help='Delete donor')
    donor_delete_parser.add_argument('--id', required=True)
    
    # donor stats
    donor_stats_parser = donor_subparsers.add_parser('stats', help='Donor statistics')
    
    # Donation commands
    donation_parser = subparsers.add_parser('donation', help='Donation management')
    donation_subparsers = donation_parser.add_subparsers(dest='donation_action')
    
    # donation list
    donation_list_parser = donation_subparsers.add_parser('list', help='List donations')
    donation_list_parser.add_argument('--donor-id', help='Filter by donor')
    donation_list_parser.add_argument('--campaign-id', help='Filter by campaign')
    donation_list_parser.add_argument('--limit', type=int)
    donation_list_parser.add_argument('--format', choices=['table', 'json', 'csv'], default='table')
    
    # donation create
    donation_create_parser = donation_subparsers.add_parser('create', help='Create donation')
    donation_create_parser.add_argument('--donor-id', required=True)
    donation_create_parser.add_argument('--amount', type=float, required=True)
    donation_create_parser.add_argument('--campaign-id')
    donation_create_parser.add_argument('--method', choices=['credit_card', 'bank_transfer', 'check', 'cash', 'crypto', 'stock', 'other'])
    donation_create_parser.add_argument('--date')
    donation_create_parser.add_argument('--completed', action='store_true')
    
    # donation summary
    donation_summary_parser = donation_subparsers.add_parser('summary', help='Donation summary')
    
    # Campaign commands
    campaign_parser = subparsers.add_parser('campaign', help='Campaign management')
    campaign_subparsers = campaign_parser.add_subparsers(dest='campaign_action')
    
    # campaign list
    campaign_list_parser = campaign_subparsers.add_parser('list', help='List campaigns')
    campaign_list_parser.add_argument('--active', action='store_true', help='Only active campaigns')
    campaign_list_parser.add_argument('--format', choices=['table', 'json', 'csv'], default='table')
    
    # campaign get
    campaign_get_parser = campaign_subparsers.add_parser('get', help='Get campaign')
    campaign_get_parser.add_argument('--id', required=True)
    campaign_get_parser.add_argument('--format', choices=['table', 'json', 'csv'], default='table')
    
    # campaign create
    campaign_create_parser = campaign_subparsers.add_parser('create', help='Create campaign')
    campaign_create_parser.add_argument('--name', required=True)
    campaign_create_parser.add_argument('--description')
    campaign_create_parser.add_argument('--type', choices=['annual', 'capital', 'emergency', 'event', 'restricted', 'unrestricted'])
    campaign_create_parser.add_argument('--goal', type=float, required=True)
    campaign_create_parser.add_argument('--start-date')
    campaign_create_parser.add_argument('--end-date')
    
    # Event commands
    event_parser = subparsers.add_parser('event', help='Event management')
    event_subparsers = event_parser.add_subparsers(dest='event_action')
    
    # event list
    event_list_parser = event_subparsers.add_parser('list', help='List events')
    event_list_parser.add_argument('--upcoming', action='store_true')
    event_list_parser.add_argument('--format', choices=['table', 'json', 'csv'], default='table')
    
    # event get
    event_get_parser = event_subparsers.add_parser('get', help='Get event')
    event_get_parser.add_argument('--id', required=True)
    event_get_parser.add_argument('--format', choices=['table', 'json', 'csv'], default='table')
    
    # Report commands
    report_parser = subparsers.add_parser('report', help='Reports')
    report_subparsers = report_parser.add_subparsers(dest='report_action')
    
    # report list
    report_list_parser = report_subparsers.add_parser('list', help='List reports')
    report_list_parser.add_argument('--format', choices=['table', 'json', 'csv'], default='table')
    
    # report run
    report_run_parser = report_subparsers.add_parser('run', help='Run report')
    report_run_parser.add_argument('report_id', help='Report ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Route to appropriate handler
    if args.command == 'donor':
        if args.donor_action == 'list':
            donor_list(args)
        elif args.donor_action == 'get':
            donor_get(args)
        elif args.donor_action == 'create':
            donor_create(args)
        elif args.donor_action == 'search':
            donor_search(args)
        elif args.donor_action == 'update':
            donor_update(args)
        elif args.donor_action == 'delete':
            donor_delete(args)
        elif args.donor_action == 'stats':
            donor_stats(args)
        else:
            donor_parser.print_help()
    
    elif args.command == 'donation':
        if args.donation_action == 'list':
            donation_list(args)
        elif args.donation_action == 'create':
            donation_create(args)
        elif args.donation_action == 'summary':
            donation_summary(args)
        else:
            donation_parser.print_help()
    
    elif args.command == 'campaign':
        if args.campaign_action == 'list':
            campaign_list(args)
        elif args.campaign_action == 'get':
            campaign_get(args)
        elif args.campaign_action == 'create':
            campaign_create(args)
        else:
            campaign_parser.print_help()
    
    elif args.command == 'event':
        if args.event_action == 'list':
            event_list(args)
        elif args.event_action == 'get':
            event_get(args)
        else:
            event_parser.print_help()
    
    elif args.command == 'report':
        if args.report_action == 'list':
            report_list(args)
        elif args.report_action == 'run':
            report_run(args)
        else:
            report_parser.print_help()


if __name__ == '__main__':
    main()
