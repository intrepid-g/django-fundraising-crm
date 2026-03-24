#!/usr/bin/env python3
"""
Django Fundraising CRM CLI

A command-line interface for managing the fundraising CRM.
Provides commands for database management, data import/export,
and administrative tasks.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add the project directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fundraising_crm.settings')


def run_django_command(args):
    """Run a Django management command."""
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py'] + args)
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc


def cmd_migrate(args):
    """Run database migrations."""
    print("🔄 Running database migrations...")
    run_django_command(['migrate'])
    print("✅ Migrations complete!")


def cmd_makemigrations(args):
    """Create new migrations."""
    print("📝 Creating migrations...")
    apps = args.apps if args.apps else []
    run_django_command(['makemigrations'] + apps)
    print("✅ Migrations created!")


def cmd_shell(args):
    """Open Django shell."""
    print("🐚 Opening Django shell...")
    run_django_command(['shell'])


def cmd_test(args):
    """Run tests."""
    print("🧪 Running tests...")
    apps = args.apps if args.apps else []
    verbosity = ['-v', str(args.verbosity)] if args.verbosity else ['-v', '1']
    run_django_command(['test'] + verbosity + apps)


def cmd_createsuperuser(args):
    """Create a superuser."""
    print("👤 Creating superuser...")
    run_django_command(['createsuperuser'])


def cmd_collectstatic(args):
    """Collect static files."""
    print("📦 Collecting static files...")
    run_django_command(['collectstatic', '--noinput'])
    print("✅ Static files collected!")


def cmd_runserver(args):
    """Run the development server."""
    host = args.host if hasattr(args, 'host') else '0.0.0.0'
    port = args.port if hasattr(args, 'port') else '8000'
    print(f"🚀 Starting development server on {host}:{port}...")
    run_django_command(['runserver', f'{host}:{port}'])


def cmd_dbshell(args):
    """Open database shell."""
    print("🗄️  Opening database shell...")
    run_django_command(['dbshell'])


def cmd_check(args):
    """Run Django system checks."""
    print("🔍 Running system checks...")
    run_django_command(['check'])
    print("✅ System checks complete!")


def cmd_dumpdata(args):
    """Dump database data to JSON."""
    output = args.output if hasattr(args, 'output') and args.output else 'dump.json'
    apps = args.apps if args.apps else []
    print(f"💾 Dumping data to {output}...")
    run_django_command(['dumpdata', '--indent', '2', '-o', output] + apps)
    print(f"✅ Data dumped to {output}!")


def cmd_loaddata(args):
    """Load data from JSON fixture."""
    if not args.fixture:
        print("❌ Error: Please specify a fixture file with -f/--fixture")
        sys.exit(1)
    print(f"📥 Loading data from {args.fixture}...")
    run_django_command(['loaddata', args.fixture])
    print("✅ Data loaded!")


def cmd_showmigrations(args):
    """Show migration status."""
    apps = args.apps if args.apps else []
    run_django_command(['showmigrations'] + apps)


def cmd_resetdb(args):
    """Reset the database (WARNING: Destroys all data!)."""
    if not args.force:
        confirm = input("⚠️  WARNING: This will delete all data! Type 'yes' to continue: ")
        if confirm != 'yes':
            print("❌ Aborted.")
            return
    
    print("🗑️  Resetting database...")
    db_path = Path(__file__).parent / 'db.sqlite3'
    if db_path.exists():
        db_path.unlink()
        print("✅ Database file removed.")
    
    run_django_command(['migrate'])
    print("✅ Database reset and migrations applied!")


def cmd_stats(args):
    """Show database statistics."""
    try:
        import django
        django.setup()
        
        from donors.models import Donor
        from donations.models import Donation
        from campaigns.models import Campaign
        from events.models import Event
        from communications.models import Communication
        
        print("\n📊 Fundraising CRM Statistics")
        print("=" * 40)
        print(f"👥 Donors: {Donor.objects.count()}")
        print(f"💰 Donations: {Donation.objects.count()}")
        print(f"📢 Campaigns: {Campaign.objects.count()}")
        print(f"🎉 Events: {Event.objects.count()}")
        print(f"💬 Communications: {Communication.objects.count()}")
        print("=" * 40)
        
        # Calculate totals
        from django.db.models import Sum
        total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
        print(f"💵 Total Donations: ${total_donations:,.2f}")
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Django Fundraising CRM CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s migrate              # Run database migrations
  %(prog)s test                 # Run all tests
  %(prog)s test donors donations -v 2  # Run tests for specific apps
  %(prog)s runserver            # Start development server
  %(prog)s stats                # Show database statistics
  %(prog)s shell                # Open Django shell
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # migrate
    migrate_parser = subparsers.add_parser('migrate', help='Run database migrations')
    
    # makemigrations
    makemigrations_parser = subparsers.add_parser('makemigrations', help='Create new migrations')
    makemigrations_parser.add_argument('apps', nargs='*', help='App names to create migrations for')
    
    # shell
    shell_parser = subparsers.add_parser('shell', help='Open Django shell')
    
    # test
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('apps', nargs='*', help='App names to test')
    test_parser.add_argument('-v', '--verbosity', type=int, default=1, choices=[0, 1, 2, 3],
                            help='Verbosity level (0-3)')
    
    # createsuperuser
    createsuperuser_parser = subparsers.add_parser('createsuperuser', help='Create a superuser')
    
    # collectstatic
    collectstatic_parser = subparsers.add_parser('collectstatic', help='Collect static files')
    
    # runserver
    runserver_parser = subparsers.add_parser('runserver', help='Run development server')
    runserver_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    runserver_parser.add_argument('--port', default='8000', help='Port to bind to (default: 8000)')
    
    # dbshell
    dbshell_parser = subparsers.add_parser('dbshell', help='Open database shell')
    
    # check
    check_parser = subparsers.add_parser('check', help='Run Django system checks')
    
    # dumpdata
    dumpdata_parser = subparsers.add_parser('dumpdata', help='Dump database data to JSON')
    dumpdata_parser.add_argument('apps', nargs='*', help='Apps to dump')
    dumpdata_parser.add_argument('-o', '--output', default='dump.json', help='Output file')
    
    # loaddata
    loaddata_parser = subparsers.add_parser('loaddata', help='Load data from JSON fixture')
    loaddata_parser.add_argument('-f', '--fixture', required=True, help='Fixture file to load')
    
    # showmigrations
    showmigrations_parser = subparsers.add_parser('showmigrations', help='Show migration status')
    showmigrations_parser.add_argument('apps', nargs='*', help='Apps to show')
    
    # resetdb
    resetdb_parser = subparsers.add_parser('resetdb', help='Reset the database (WARNING: Destroys all data!)')
    resetdb_parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    
    # stats
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Map commands to functions
    commands = {
        'migrate': cmd_migrate,
        'makemigrations': cmd_makemigrations,
        'shell': cmd_shell,
        'test': cmd_test,
        'createsuperuser': cmd_createsuperuser,
        'collectstatic': cmd_collectstatic,
        'runserver': cmd_runserver,
        'dbshell': cmd_dbshell,
        'check': cmd_check,
        'dumpdata': cmd_dumpdata,
        'loaddata': cmd_loaddata,
        'showmigrations': cmd_showmigrations,
        'resetdb': cmd_resetdb,
        'stats': cmd_stats,
    }
    
    command_func = commands.get(args.command)
    if command_func:
        command_func(args)
    else:
        print(f"❌ Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
