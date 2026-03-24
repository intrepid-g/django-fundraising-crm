"""
Pytest configuration and shared fixtures for django-fundraising-crm tests
"""
import pytest
import os
import django
from django.conf import settings

# Configure Django settings for tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fundraising_crm.settings')

# Add pytest-django marker
pytest_plugins = ['pytest_django']


@pytest.fixture(scope='session')
def django_db_setup():
    """Configure test database"""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }


@pytest.fixture
def api_client():
    """Return API test client"""
    from django.test import Client
    return Client(content_type='application/json')


@pytest.fixture
def authenticated_client(db):
    """Return authenticated API test client"""
    from django.test import Client
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def admin_client(db):
    """Return admin authenticated API test client"""
    from django.test import Client
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )
    client = Client()
    client.force_login(user)
    return client


# =============================================================================
# DONOR FIXTURES
# =============================================================================

@pytest.fixture
def donor(db):
    """Create a single donor"""
    from factories import DonorFactory
    return DonorFactory()


@pytest.fixture
def donors(db):
    """Create multiple donors"""
    from factories import DonorFactory
    return DonorFactory.create_batch(5)


@pytest.fixture
def donor_tag(db):
    """Create a donor tag"""
    from factories import DonorTagFactory
    return DonorTagFactory()


@pytest.fixture
def donor_note(db, donor):
    """Create a donor note attached to a donor"""
    from factories import DonorNoteFactory
    return DonorNoteFactory(donor=donor)


@pytest.fixture
def donor_relationship(db, donor):
    """Create a donor relationship"""
    from factories import DonorRelationshipFactory
    from factories import DonorFactory
    other_donor = DonorFactory()
    return DonorRelationshipFactory(from_donor=donor, to_donor=other_donor)


# =============================================================================
# DONATION FIXTURES
# =============================================================================

@pytest.fixture
def donation(db, donor):
    """Create a single donation"""
    from factories import DonationFactory
    return DonationFactory(donor=donor)


@pytest.fixture
def donations(db, donor):
    """Create multiple donations for a donor"""
    from factories import DonationFactory
    return DonationFactory.create_batch(3, donor=donor)


@pytest.fixture
def recurring_donation(db, donor):
    """Create a recurring donation"""
    from factories import RecurringDonationFactory
    return RecurringDonationFactory(donor=donor)


@pytest.fixture
def pledge(db, donor):
    """Create a pledge"""
    from factories import PledgeFactory
    return PledgeFactory(donor=donor)


# =============================================================================
# EVENT FIXTURES
# =============================================================================

@pytest.fixture
def event(db):
    """Create a single event"""
    from factories import EventFactory
    return EventFactory()


@pytest.fixture
def events(db):
    """Create multiple events"""
    from factories import EventFactory
    return EventFactory.create_batch(3)


@pytest.fixture
def event_registration(db, event, donor):
    """Create an event registration"""
    from factories import EventRegistrationFactory
    return EventRegistrationFactory(event=event, donor=donor)


@pytest.fixture
def event_sponsor(db, event, donor):
    """Create an event sponsor"""
    from factories import EventSponsorFactory
    return EventSponsorFactory(event=event, donor=donor)


@pytest.fixture
def event_task(db, event):
    """Create an event task"""
    from factories import EventTaskFactory
    return EventTaskFactory(event=event)


# =============================================================================
# COMMUNICATION FIXTURES
# =============================================================================

@pytest.fixture
def communication(db, donor):
    """Create a single communication"""
    from factories import CommunicationFactory
    return CommunicationFactory(donor=donor)


@pytest.fixture
def communications(db, donor):
    """Create multiple communications"""
    from factories import CommunicationFactory
    return CommunicationFactory.create_batch(3, donor=donor)


@pytest.fixture
def communication_template(db):
    """Create a communication template"""
    from factories import CommunicationTemplateFactory
    return CommunicationTemplateFactory()


@pytest.fixture
def communication_schedule(db, donor, communication_template):
    """Create a scheduled communication"""
    from factories import CommunicationScheduleFactory
    return CommunicationScheduleFactory(donor=donor, template=communication_template)


@pytest.fixture
def communication_preference(db, donor):
    """Create communication preferences for a donor"""
    from factories import CommunicationPreferenceFactory
    return CommunicationPreferenceFactory(donor=donor)


@pytest.fixture
def call_log(db, donor, communication):
    """Create a call log"""
    from factories import CallLogFactory
    return CallLogFactory(donor=donor, communication=communication)


# =============================================================================
# REPORT FIXTURES
# =============================================================================

@pytest.fixture
def report(db):
    """Create a single report"""
    from factories import ReportFactory
    return ReportFactory()


@pytest.fixture
def dashboard(db):
    """Create a dashboard"""
    from factories import DashboardFactory
    return DashboardFactory()


@pytest.fixture
def report_execution(db, report):
    """Create a report execution"""
    from factories import ReportExecutionFactory
    return ReportExecutionFactory(report=report)


@pytest.fixture
def metric_definition(db):
    """Create a metric definition"""
    from factories import MetricDefinitionFactory
    return MetricDefinitionFactory()


# =============================================================================
# COMPLEX FIXTURES
# =============================================================================

@pytest.fixture
def donor_with_donations(db):
    """Create a donor with multiple donations"""
    from factories import DonorFactory, DonationFactory
    donor = DonorFactory()
    donations = DonationFactory.create_batch(3, donor=donor)
    return donor, donations


@pytest.fixture
def event_with_registrations(db):
    """Create an event with multiple registrations"""
    from factories import EventFactory, EventRegistrationFactory, DonorFactory
    event = EventFactory()
    donors = DonorFactory.create_batch(5)
    registrations = [
        EventRegistrationFactory(event=event, donor=donor)
        for donor in donors
    ]
    return event, registrations


@pytest.fixture
def donor_with_communications(db):
    """Create a donor with multiple communications"""
    from factories import DonorFactory, CommunicationFactory
    donor = DonorFactory()
    communications = CommunicationFactory.create_batch(5, donor=donor)
    return donor, communications
