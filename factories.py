"""
Test data factories for django-fundraising-crm
Uses Factory Boy with Faker for realistic test data generation
"""
from datetime import timedelta

import factory
from factory.django import DjangoModelFactory
from faker import Faker

# Import all models
from donors.models import Donor
from donations.models import Donation, RecurringDonation
from events.models import Event, EventRegistration, EventSponsor, EventTask
from communications.models import (
    Communication, CommunicationTemplate, CommunicationSchedule,
    CommunicationPreference, CallLog
)
from reports.models import Report, Dashboard, ReportExecution, MetricDefinition

faker = Faker()


# =============================================================================
# DONORS FACTORIES
# =============================================================================

class DonorFactory(DjangoModelFactory):
    class Meta:
        model = Donor
    
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    
    # Donor classification
    donor_type = factory.Iterator(['individual', 'corporate', 'foundation'])
    
    # Timestamps
    created_at = factory.Faker('date_time_this_year')
    updated_at = factory.Faker('date_time_this_year')


# =============================================================================
# DONATIONS FACTORIES
# =============================================================================

class DonationFactory(DjangoModelFactory):
    class Meta:
        model = Donation
    
    donor = factory.SubFactory(DonorFactory)
    amount = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    currency = factory.Iterator(['USD', 'EUR', 'GBP'])
    
    # Donation details
    status = factory.Iterator(['pending', 'completed', 'failed', 'refunded'])
    
    # Payment info
    payment_method = factory.Iterator(['credit_card', 'bank_transfer', 'check', 'cash', 'crypto'])
    transaction_id = factory.Faker('uuid4')
    
    # Campaign/event tracking
    campaign = factory.Faker('word')
    
    # Receipt
    receipt_sent = factory.Faker('boolean')
    
    # Notes
    notes = factory.Faker('text', max_nb_chars=200)
    
    # Timestamps
    donation_date = factory.Faker('date_time_this_year')
    created_at = factory.Faker('date_time_this_year')


class RecurringDonationFactory(DjangoModelFactory):
    class Meta:
        model = RecurringDonation
    
    donor = factory.SubFactory(DonorFactory)
    amount = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    currency = factory.Iterator(['USD', 'EUR', 'GBP'])
    
    # Recurrence settings
    frequency = factory.Iterator(['weekly', 'monthly', 'quarterly', 'yearly'])
    start_date = factory.Faker('date_this_year')
    end_date = factory.Faker('date_this_year')
    
    # Status
    status = factory.Iterator(['active', 'paused', 'cancelled', 'completed'])
    
    # Payment
    payment_method = factory.Iterator(['credit_card', 'bank_transfer'])
    
    # Tracking
    total_donations = factory.Faker('pyint', min_value=0, max_value=50)
    total_amount = factory.Faker('pydecimal', left_digits=6, right_digits=2, positive=True)
    
    created_at = factory.Faker('date_time_this_year')


# =============================================================================
# EVENTS FACTORIES
# =============================================================================

class EventFactory(DjangoModelFactory):
    class Meta:
        model = Event
    
    name = factory.Faker('catch_phrase')
    description = factory.Faker('paragraph')
    event_type = factory.Iterator(['gala', 'dinner', 'auction', 'golf_tournament', 'walkathon', 'concert', 'meeting', 'other'])
    status = factory.Iterator(['draft', 'planning', 'confirmed', 'in_progress', 'completed', 'cancelled'])
    
    # Dates - ensure end_date is after start_date
    start_date = factory.Faker('date_time_this_year')
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(hours=2))
    setup_date = factory.LazyAttribute(lambda o: o.start_date - timedelta(hours=1))
    
    # Location
    venue_name = factory.Faker('company')
    venue_address = factory.Faker('street_address')
    venue_city = factory.Faker('city')
    venue_state = factory.Faker('state_abbr')
    venue_postal_code = factory.Faker('zipcode')
    venue_country = factory.Iterator(['US', 'CA', 'UK'])
    virtual_event_url = factory.Faker('url')
    is_virtual = factory.Faker('boolean')
    
    # Capacity and registration
    capacity = factory.Faker('pyint', min_value=10, max_value=500)
    registration_deadline = factory.Faker('date_time_this_year')
    requires_registration = factory.Faker('boolean')
    is_invite_only = factory.Faker('boolean')
    
    # Financial
    fundraising_goal = factory.Faker('pydecimal', left_digits=6, right_digits=2, positive=True)
    ticket_price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    sponsor_goal = factory.Faker('pydecimal', left_digits=6, right_digits=2, positive=True)
    
    # Tracking
    actual_attendees = factory.Faker('pyint', min_value=0, max_value=500)
    total_raised = factory.Faker('pydecimal', left_digits=6, right_digits=2, positive=True)
    total_expenses = factory.Faker('pydecimal', left_digits=6, right_digits=2, positive=True)
    
    # Notes
    notes = factory.Faker('paragraph')
    custom_fields = factory.LazyFunction(lambda: {})
    
    created_at = factory.Faker('date_time_this_year')


class EventRegistrationFactory(DjangoModelFactory):
    class Meta:
        model = EventRegistration
    
    event = factory.SubFactory(EventFactory)
    donor = factory.SubFactory(DonorFactory)
    
    # Registration details
    registration_date = factory.Faker('date_time_this_year')
    status = factory.Iterator(['registered', 'confirmed', 'attended', 'no_show', 'cancelled'])
    
    # Attendee info (may differ from donor)
    attendee_name = factory.Faker('name')
    attendee_email = factory.Faker('email')
    
    # Payment
    ticket_price_paid = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    payment_status = factory.Iterator(['pending', 'paid', 'waived', 'refunded'])
    
    # Check-in
    checked_in = factory.Faker('boolean')
    check_in_time = factory.Faker('date_time_this_year')
    
    # Dietary/needs
    dietary_restrictions = factory.Faker('sentence')
    special_requests = factory.Faker('sentence')
    
    created_at = factory.Faker('date_time_this_year')


class EventSponsorFactory(DjangoModelFactory):
    class Meta:
        model = EventSponsor
    
    event = factory.SubFactory(EventFactory)
    donor = factory.SubFactory(DonorFactory)
    
    # Sponsor details
    sponsor_name = factory.Faker('company')
    sponsorship_level = factory.Iterator(['platinum', 'gold', 'silver', 'bronze'])
    sponsorship_amount = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    
    # Benefits
    logo_on_materials = factory.Faker('boolean')
    speaking_opportunity = factory.Faker('boolean')
    table_included = factory.Faker('boolean')
    tickets_included = factory.Faker('pyint', min_value=0, max_value=10)
    
    # Status
    status = factory.Iterator(['pending', 'confirmed', 'delivered'])
    
    # Contact
    contact_name = factory.Faker('name')
    contact_email = factory.Faker('email')
    contact_phone = factory.Faker('phone_number')
    
    created_at = factory.Faker('date_time_this_year')


class EventTaskFactory(DjangoModelFactory):
    class Meta:
        model = EventTask
    
    event = factory.SubFactory(EventFactory)
    
    # Task details
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('paragraph')
    
    # Assignment
    assigned_to = factory.Faker('name')
    
    # Dates
    due_date = factory.Faker('date_time_this_year')
    completed_date = factory.Faker('date_time_this_year')
    
    # Status
    status = factory.Iterator(['pending', 'in_progress', 'completed', 'cancelled'])
    priority = factory.Iterator(['low', 'medium', 'high', 'urgent'])
    
    created_at = factory.Faker('date_time_this_year')


# =============================================================================
# COMMUNICATIONS FACTORIES
# =============================================================================

class CommunicationFactory(DjangoModelFactory):
    class Meta:
        model = Communication
    
    donor = factory.SubFactory(DonorFactory)
    
    # Communication details
    communication_type = factory.Iterator(['email', 'phone', 'sms', 'meeting', 'note', 'mail'])
    subject = factory.Faker('sentence', nb_words=6)
    content = factory.Faker('paragraph')
    
    # Direction
    direction = factory.Iterator(['inbound', 'outbound'])
    
    # Status
    status = factory.Iterator(['draft', 'sent', 'delivered', 'read', 'failed'])
    
    # Timestamps
    sent_at = factory.Faker('date_time_this_year')
    received_at = factory.Faker('date_time_this_year')
    
    # Follow-up
    requires_follow_up = factory.Faker('boolean')
    follow_up_date = factory.Faker('date_this_year')
    
    # Campaign tracking
    campaign = factory.Faker('word')
    
    created_at = factory.Faker('date_time_this_year')


class CommunicationTemplateFactory(DjangoModelFactory):
    class Meta:
        model = CommunicationTemplate
    
    name = factory.Faker('catch_phrase')
    template_type = factory.Iterator(['email', 'sms', 'letter'])
    
    # Content
    subject_template = factory.Faker('sentence', nb_words=6)
    body_template = factory.Faker('paragraph')
    
    # Variables (stored as JSON list)
    variables = factory.LazyFunction(lambda: ['{{donor_name}}', '{{amount}}', '{{event_name}}'])
    
    # Usage
    is_active = factory.Faker('boolean')
    usage_count = factory.Faker('pyint', min_value=0, max_value=100)
    
    created_at = factory.Faker('date_time_this_year')


class CommunicationScheduleFactory(DjangoModelFactory):
    class Meta:
        model = CommunicationSchedule
    
    donor = factory.SubFactory(DonorFactory)
    template = factory.SubFactory(CommunicationTemplateFactory)
    
    # Schedule details
    scheduled_date = factory.Faker('date_time_this_year')
    status = factory.Iterator(['scheduled', 'sent', 'cancelled', 'failed'])
    
    # Variable values (JSON)
    variable_values = factory.LazyFunction(lambda: {'donor_name': 'John Doe', 'amount': '$100'})
    
    # Actual send time
    sent_at = factory.Faker('date_time_this_year')
    
    created_at = factory.Faker('date_time_this_year')


class CommunicationPreferenceFactory(DjangoModelFactory):
    class Meta:
        model = CommunicationPreference
    
    donor = factory.SubFactory(DonorFactory)
    
    # Channel preferences
    email_opt_in = factory.Faker('boolean')
    phone_opt_in = factory.Faker('boolean')
    sms_opt_in = factory.Faker('boolean')
    mail_opt_in = factory.Faker('boolean')
    
    # Do Not Contact
    do_not_contact = factory.Faker('boolean')
    do_not_contact_reason = factory.Faker('sentence')
    do_not_contact_until = factory.Faker('date_this_year')
    
    # Frequency
    preferred_frequency = factory.Iterator(['weekly', 'monthly', 'quarterly', 'yearly', 'as_needed'])
    
    created_at = factory.Faker('date_time_this_year')


class CallLogFactory(DjangoModelFactory):
    class Meta:
        model = CallLog
    
    donor = factory.SubFactory(DonorFactory)
    communication = factory.SubFactory(CommunicationFactory)
    
    # Call details
    phone_number = factory.Faker('phone_number')
    direction = factory.Iterator(['inbound', 'outbound'])
    
    # Duration (seconds)
    duration = factory.Faker('pyint', min_value=30, max_value=3600)
    
    # Outcome
    outcome = factory.Iterator(['answered', 'voicemail', 'no_answer', 'busy', 'failed'])
    
    # Notes
    notes = factory.Faker('paragraph')
    
    # Follow-up
    follow_up_required = factory.Faker('boolean')
    follow_up_date = factory.Faker('date_this_year')
    
    created_at = factory.Faker('date_time_this_year')


# =============================================================================
# REPORTS FACTORIES
# =============================================================================

class ReportFactory(DjangoModelFactory):
    class Meta:
        model = Report
    
    name = factory.Faker('catch_phrase')
    description = factory.Faker('paragraph')
    report_type = factory.Iterator(['donor_summary', 'donation_analysis', 'event_report', 'campaign_report', 'custom'])
    
    # Query/filters (stored as JSON)
    filters = factory.LazyFunction(lambda: {'date_from': '2024-01-01', 'date_to': '2024-12-31'})
    
    # Output format
    output_format = factory.Iterator(['table', 'chart', 'csv', 'pdf'])
    
    # Scheduling
    is_scheduled = factory.Faker('boolean')
    schedule_frequency = factory.Iterator(['daily', 'weekly', 'monthly', 'quarterly'])
    
    # Creator
    created_by = factory.Faker('name')
    
    is_active = factory.Faker('boolean')
    created_at = factory.Faker('date_time_this_year')


class DashboardFactory(DjangoModelFactory):
    class Meta:
        model = Dashboard
    
    name = factory.Faker('catch_phrase')
    description = factory.Faker('sentence')
    
    # Widgets configuration (JSON)
    widgets = factory.LazyFunction(lambda: [
        {'type': 'stat', 'metric': 'total_donors'},
        {'type': 'chart', 'metric': 'donations_over_time'},
        {'type': 'table', 'metric': 'recent_donations'}
    ])
    
    # Layout
    layout = factory.Iterator(['grid', 'list', 'custom'])
    
    # Sharing
    is_shared = factory.Faker('boolean')
    shared_with = factory.LazyFunction(lambda: ['user1', 'user2'])
    
    # Creator
    created_by = factory.Faker('name')
    
    is_active = factory.Faker('boolean')
    created_at = factory.Faker('date_time_this_year')


class ReportExecutionFactory(DjangoModelFactory):
    class Meta:
        model = ReportExecution
    
    report = factory.SubFactory(ReportFactory)
    
    # Execution details
    executed_by = factory.Faker('name')
    started_at = factory.Faker('date_time_this_year')
    completed_at = factory.Faker('date_time_this_year')
    
    # Status
    status = factory.Iterator(['running', 'completed', 'failed', 'cancelled'])
    
    # Results
    row_count = factory.Faker('pyint', min_value=0, max_value=10000)
    result_data = factory.LazyFunction(lambda: {'summary': {'total': 1000}})
    
    # Error info
    error_message = factory.Faker('sentence')
    
    created_at = factory.Faker('date_time_this_year')


class MetricDefinitionFactory(DjangoModelFactory):
    class Meta:
        model = MetricDefinition
    
    name = factory.Faker('catch_phrase')
    description = factory.Faker('sentence')
    
    # Calculation
    calculation_type = factory.Iterator(['sum', 'count', 'average', 'min', 'max', 'custom'])
    formula = factory.Faker('sentence')
    
    # Data source
    model_name = factory.Iterator(['Donation', 'Donor', 'Event', 'Communication'])
    field_name = factory.Iterator(['amount', 'id', 'created_at'])
    
    # Filters (JSON)
    filters = factory.LazyFunction(lambda: {'status': 'completed'})
    
    # Display
    display_format = factory.Iterator(['number', 'currency', 'percentage', 'date'])
    
    is_active = factory.Faker('boolean')
    created_at = factory.Faker('date_time_this_year')


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_test_donor_with_donations(donation_count=3):
    """Create a donor with multiple donations for testing"""
    donor = DonorFactory()
    donations = DonationFactory.create_batch(donation_count, donor=donor)
    return donor, donations


def create_test_event_with_registrations(registration_count=5):
    """Create an event with multiple registrations for testing"""
    event = EventFactory()
    registrations = EventRegistrationFactory.create_batch(registration_count, event=event)
    return event, registrations


def create_test_donor_with_communications(communication_count=5):
    """Create a donor with multiple communications for testing"""
    donor = DonorFactory()
    communications = CommunicationFactory.create_batch(communication_count, donor=donor)
    return donor, communications
