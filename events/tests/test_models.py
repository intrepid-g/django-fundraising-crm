"""
Events app model tests
Comprehensive unit tests for all event-related models
"""
import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from events.models import Event, EventRegistration, EventSponsor, EventTask
from factories import (
    DonorFactory, EventFactory, EventRegistrationFactory,
    EventSponsorFactory, EventTaskFactory
)


# =============================================================================
# EVENT MODEL TESTS
# =============================================================================

@pytest.mark.django_db
class TestEventModel:
    """Test cases for the Event model"""
    
    def test_create_event_with_valid_data(self):
        """Test creating an event with valid data"""
        event = EventFactory(
            name='Annual Gala',
            event_type='gala',
            capacity=200
        )
        
        assert event.id is not None
        assert event.name == 'Annual Gala'
        assert event.event_type == 'gala'
        assert event.capacity == 200
    
    def test_event_str_representation(self):
        """Test the string representation of an event"""
        event = EventFactory(name='Charity Dinner')
        assert 'Charity Dinner' in str(event)
    
    def test_event_type_choices(self):
        """Test event type choices"""
        for event_type in ['gala', 'auction', 'dinner', 'meeting', 'webinar', 'fundraiser']:
            event = EventFactory(event_type=event_type)
            assert event.event_type == event_type
    
    def test_event_status_choices(self):
        """Test event status choices"""
        for status in ['planning', 'open', 'closed', 'ongoing', 'completed', 'cancelled']:
            event = EventFactory(status=status)
            assert event.status == status
    
    def test_event_dates(self):
        """Test event date fields"""
        from datetime import datetime
        
        event = EventFactory(
            start_date='2024-06-15 18:00:00',
            end_date='2024-06-15 22:00:00'
        )
        
        assert event.start_date is not None
        assert event.end_date is not None
    
    def test_event_capacity_positive(self):
        """Test that event capacity must be positive"""
        with pytest.raises(Exception):
            EventFactory(capacity=-10)
    
    def test_event_capacity_zero(self):
        """Test that event capacity can be zero (unlimited)"""
        event = EventFactory(capacity=0)
        assert event.capacity == 0
    
    def test_event_location_fields(self):
        """Test event location fields"""
        event = EventFactory(
            location='123 Main St, City',
            venue='Grand Ballroom'
        )
        
        assert event.location == '123 Main St, City'
        assert event.venue == 'Grand Ballroom'
    
    def test_event_financial_fields(self):
        """Test event financial fields"""
        event = EventFactory(
            ticket_price=Decimal('100.00'),
            fundraising_goal=Decimal('50000.00')
        )
        
        assert event.ticket_price == Decimal('100.00')
        assert event.fundraising_goal == Decimal('50000.00')
    
    def test_event_registration_settings(self):
        """Test event registration settings"""
        event = EventFactory(
            registration_required=True,
            registration_deadline='2024-06-10 23:59:59'
        )
        
        assert event.registration_required is True
        assert event.registration_deadline is not None
    
    def test_event_contact_info(self):
        """Test event contact information"""
        event = EventFactory(
            organizer='Event Coordinator',
            contact_email='events@example.com',
            contact_phone='555-1234'
        )
        
        assert event.organizer == 'Event Coordinator'
        assert event.contact_email == 'events@example.com'
        assert event.contact_phone == '555-1234'
    
    def test_event_description_field(self):
        """Test event description field"""
        event = EventFactory(description='Join us for an evening of giving')
        assert event.description == 'Join us for an evening of giving'
    
    def test_event_timestamps(self):
        """Test event timestamps"""
        event = EventFactory()
        assert event.created_at is not None
        assert event.updated_at is not None
    
    def test_event_update_fields(self):
        """Test updating event fields"""
        event = EventFactory(name='Old Name', capacity=100)
        
        event.name = 'New Name'
        event.capacity = 150
        event.save()
        
        updated_event = Event.objects.get(id=event.id)
        assert updated_event.name == 'New Name'
        assert updated_event.capacity == 150
    
    def test_event_delete(self):
        """Test deleting an event"""
        event = EventFactory()
        event_id = event.id
        event.delete()
        
        with pytest.raises(Event.DoesNotExist):
            Event.objects.get(id=event_id)


# =============================================================================
# EVENT REGISTRATION MODEL TESTS
# =============================================================================

@pytest.mark.django_db
class TestEventRegistrationModel:
    """Test cases for the EventRegistration model"""
    
    def test_create_registration_with_valid_data(self):
        """Test creating an event registration with valid data"""
        event = EventFactory()
        donor = DonorFactory()
        
        registration = EventRegistrationFactory(
            event=event,
            donor=donor,
            status='registered'
        )
        
        assert registration.id is not None
        assert registration.event == event
        assert registration.donor == donor
        assert registration.status == 'registered'
    
    def test_registration_str_representation(self):
        """Test the string representation of a registration"""
        event = EventFactory(name='Gala 2024')
        donor = DonorFactory(first_name='John', last_name='Doe')
        
        registration = EventRegistrationFactory(event=event, donor=donor)
        str_repr = str(registration)
        
        assert 'Gala 2024' in str_repr or 'John Doe' in str_repr
    
    def test_registration_status_choices(self):
        """Test registration status choices and workflow"""
        event = EventFactory()
        donor = DonorFactory()
        
        for status in ['registered', 'confirmed', 'attended', 'no_show', 'cancelled']:
            registration = EventRegistrationFactory(
                event=event,
                donor=donor,
                status=status
            )
            assert registration.status == status
    
    def test_registration_status_workflow(self):
        """Test the registration status workflow"""
        event = EventFactory()
        donor = DonorFactory()
        
        # Start as registered
        registration = EventRegistrationFactory(
            event=event,
            donor=donor,
            status='registered'
        )
        assert registration.status == 'registered'
        
        # Move to confirmed
        registration.status = 'confirmed'
        registration.save()
        assert EventRegistration.objects.get(id=registration.id).status == 'confirmed'
        
        # Mark as attended
        registration.status = 'attended'
        registration.checked_in = True
        registration.check_in_time = '2024-06-15 19:00:00'
        registration.save()
        
        attended = EventRegistration.objects.get(id=registration.id)
        assert attended.status == 'attended'
        assert attended.checked_in is True
    
    def test_registration_attendee_info(self):
        """Test registration attendee information"""
        event = EventFactory()
        donor = DonorFactory(first_name='Donor', last_name='Name')
        
        registration = EventRegistrationFactory(
            event=event,
            donor=donor,
            attendee_name='Guest Name',
            attendee_email='guest@example.com'
        )
        
        assert registration.attendee_name == 'Guest Name'
        assert registration.attendee_email == 'guest@example.com'
    
    def test_registration_payment_fields(self):
        """Test registration payment fields"""
        event = EventFactory()
        donor = DonorFactory()
        
        registration = EventRegistrationFactory(
            event=event,
            donor=donor,
            ticket_price_paid=Decimal('100.00'),
            payment_status='paid'
        )
        
        assert registration.ticket_price_paid == Decimal('100.00')
        assert registration.payment_status == 'paid'
    
    def test_registration_check_in(self):
        """Test registration check-in functionality"""
        event = EventFactory()
        donor = DonorFactory()
        
        registration = EventRegistrationFactory(
            event=event,
            donor=donor,
            checked_in=True,
            check_in_time='2024-06-15 18:30:00'
        )
        
        assert registration.checked_in is True
        assert registration.check_in_time is not None
    
    def test_registration_dietary_restrictions(self):
        """Test registration dietary restrictions field"""
        event = EventFactory()
        donor = DonorFactory()
        
        registration = EventRegistrationFactory(
            event=event,
            donor=donor,
            dietary_restrictions='Vegetarian, no nuts',
            special_requests='Near the stage please'
        )
        
        assert registration.dietary_restrictions == 'Vegetarian, no nuts'
        assert registration.special_requests == 'Near the stage please'
    
    def test_registration_unique_constraint(self):
        """Test that a donor can only have one registration per event"""
        event = EventFactory()
        donor = DonorFactory()
        
        registration1 = EventRegistrationFactory(event=event, donor=donor)
        
        # Attempting to create another registration should fail
        with pytest.raises(Exception):
            EventRegistrationFactory(event=event, donor=donor)
    
    def test_registration_cascade_delete_event(self):
        """Test that registrations are deleted when event is deleted"""
        event = EventFactory()
        donor = DonorFactory()
        registration = EventRegistrationFactory(event=event, donor=donor)
        reg_id = registration.id
        
        event.delete()
        
        with pytest.raises(EventRegistration.DoesNotExist):
            EventRegistration.objects.get(id=reg_id)
    
    def test_registration_cascade_delete_donor(self):
        """Test that registrations are deleted when donor is deleted"""
        event = EventFactory()
        donor = DonorFactory()
        registration = EventRegistrationFactory(event=event, donor=donor)
        reg_id = registration.id
        
        donor.delete()
        
        with pytest.raises(EventRegistration.DoesNotExist):
            EventRegistration.objects.get(id=reg_id)
    
    def test_event_registration_count(self):
        """Test counting registrations for an event"""
        event = EventFactory()
        donors = [DonorFactory() for _ in range(5)]
        
        for donor in donors:
            EventRegistrationFactory(event=event, donor=donor)
        
        assert event.registrations.count() == 5


# =============================================================================
# EVENT SPONSOR MODEL TESTS
# =============================================================================

@pytest.mark.django_db
class TestEventSponsorModel:
    """Test cases for the EventSponsor model"""
    
    def test_create_sponsor_with_valid_data(self):
        """Test creating an event sponsor with valid data"""
        event = EventFactory()
        donor = DonorFactory()
        
        sponsor = EventSponsorFactory(
            event=event,
            donor=donor,
            sponsorship_level='gold',
            sponsorship_amount=Decimal('5000.00')
        )
        
        assert sponsor.id is not None
        assert sponsor.event == event
        assert sponsor.donor == donor
        assert sponsor.sponsorship_level == 'gold'
        assert sponsor.sponsorship_amount == Decimal('5000.00')
    
    def test_sponsor_str_representation(self):
        """Test the string representation of a sponsor"""
        event = EventFactory(name='Gala 2024')
        donor = DonorFactory(first_name='Corp', last_name='Inc')
        
        sponsor = EventSponsorFactory(
            event=event,
            donor=donor,
            sponsor_name='Acme Corporation'
        )
        
        str_repr = str(sponsor)
        assert 'Acme Corporation' in str_repr or 'Gala 2024' in str_repr
    
    def test_sponsor_level_choices(self):
        """Test sponsorship level choices"""
        event = EventFactory()
        donor = DonorFactory()
        
        for level in ['platinum', 'gold', 'silver', 'bronze']:
            sponsor = EventSponsorFactory(
                event=event,
                donor=donor,
                sponsorship_level=level
            )
            assert sponsor.sponsorship_level == level
    
    def test_sponsor_benefits_fields(self):
        """Test sponsor benefits fields"""
        event = EventFactory()
        donor = DonorFactory()
        
        sponsor = EventSponsorFactory(
            event=event,
            donor=donor,
            logo_on_materials=True,
            speaking_opportunity=True,
            table_included=True,
            tickets_included=10
        )
        
        assert sponsor.logo_on_materials is True
        assert sponsor.speaking_opportunity is True
        assert sponsor.table_included is True
        assert sponsor.tickets_included == 10
    
    def test_sponsor_status_choices(self):
        """Test sponsor status choices"""
        event = EventFactory()
        donor = DonorFactory()
        
        for status in ['pending', 'confirmed', 'delivered']:
            sponsor = EventSponsorFactory(
                event=event,
                donor=donor,
                status=status
            )
            assert sponsor.status == status
    
    def test_sponsor_contact_info(self):
        """Test sponsor contact information"""
        event = EventFactory()
        donor = DonorFactory()
        
        sponsor = EventSponsorFactory(
            event=event,
            donor=donor,
            contact_name='Sponsor Contact',
            contact_email='sponsor@example.com',
            contact_phone='555-5678'
        )
        
        assert sponsor.contact_name == 'Sponsor Contact'
        assert sponsor.contact_email == 'sponsor@example.com'
        assert sponsor.contact_phone == '555-5678'
    
    def test_sponsor_cascade_delete_event(self):
        """Test that sponsors are deleted when event is deleted"""
        event = EventFactory()
        donor = DonorFactory()
        sponsor = EventSponsorFactory(event=event, donor=donor)
        sponsor_id = sponsor.id
        
        event.delete()
        
        with pytest.raises(EventSponsor.DoesNotExist):
            EventSponsor.objects.get(id=sponsor_id)
    
    def test_sponsor_cascade_delete_donor(self):
        """Test that sponsors are deleted when donor is deleted"""
        event = EventFactory()
        donor = DonorFactory()
        sponsor = EventSponsorFactory(event=event, donor=donor)
        sponsor_id = sponsor.id
        
        donor.delete()
        
        with pytest.raises(EventSponsor.DoesNotExist):
            EventSponsor.objects.get(id=sponsor_id)
    
    def test_event_multiple_sponsors(self):
        """Test an event with multiple sponsors"""
        event = EventFactory()
        
        platinum = EventSponsorFactory(event=event, sponsorship_level='platinum')
        gold1 = EventSponsorFactory(event=event, sponsorship_level='gold')
        gold2 = EventSponsorFactory(event=event, sponsorship_level='gold')
        silver = EventSponsorFactory(event=event, sponsorship_level='silver')
        
        assert event.sponsors.count() == 4
        assert event.sponsors.filter(sponsorship_level='platinum').count() == 1
        assert event.sponsors.filter(sponsorship_level='gold').count() == 2


# =============================================================================
# EVENT TASK MODEL TESTS
# =============================================================================

@pytest.mark.django_db
class TestEventTaskModel:
    """Test cases for the EventTask model"""
    
    def test_create_task_with_valid_data(self):
        """Test creating an event task with valid data"""
        event = EventFactory()
        
        task = EventTaskFactory(
            event=event,
            title='Book venue',
            status='pending'
        )
        
        assert task.id is not None
        assert task.event == event
        assert task.title == 'Book venue'
        assert task.status == 'pending'
    
    def test_task_str_representation(self):
        """Test the string representation of a task"""
        event = EventFactory(name='Gala 2024')
        task = EventTaskFactory(event=event, title='Send invitations')
        
        str_repr = str(task)
        assert 'Send invitations' in str_repr
    
    def test_task_status_choices(self):
        """Test task status choices"""
        event = EventFactory()
        
        for status in ['pending', 'in_progress', 'completed', 'cancelled']:
            task = EventTaskFactory(event=event, status=status)
            assert task.status == status
    
    def test_task_priority_choices(self):
        """Test task priority choices"""
        event = EventFactory()
        
        for priority in ['low', 'medium', 'high', 'urgent']:
            task = EventTaskFactory(event=event, priority=priority)
            assert task.priority == priority
    
    def test_task_assignment(self):
        """Test task assignment field"""
        event = EventFactory()
        task = EventTaskFactory(event=event, assigned_to='Event Coordinator')
        
        assert task.assigned_to == 'Event Coordinator'
    
    def test_task_dates(self):
        """Test task date fields"""
        event = EventFactory()
        task = EventTaskFactory(
            event=event,
            due_date='2024-05-01 12:00:00',
            completed_date='2024-04-28 10:00:00'
        )
        
        assert task.due_date is not None
        assert task.completed_date is not None
    
    def test_task_description_field(self):
        """Test task description field"""
        event = EventFactory()
        task = EventTaskFactory(
            event=event,
            description='Contact venue manager to confirm booking'
        )
        
        assert task.description == 'Contact venue manager to confirm booking'
    
    def test_task_status_workflow(self):
        """Test task status workflow"""
        event = EventFactory()
        task = EventTaskFactory(event=event, status='pending')
        
        # Move to in_progress
        task.status = 'in_progress'
        task.save()
        assert EventTask.objects.get(id=task.id).status == 'in_progress'
        
        # Complete the task
        task.status = 'completed'
        task.completed_date = '2024-06-01 15:00:00'
        task.save()
        
        completed_task = EventTask.objects.get(id=task.id)
        assert completed_task.status == 'completed'
        assert completed_task.completed_date is not None
    
    def test_task_cascade_delete_event(self):
        """Test that tasks are deleted when event is deleted"""
        event = EventFactory()
        task = EventTaskFactory(event=event)
        task_id = task.id
        
        event.delete()
        
        with pytest.raises(EventTask.DoesNotExist):
            EventTask.objects.get(id=task_id)
    
    def test_event_multiple_tasks(self):
        """Test an event with multiple tasks"""
        event = EventFactory()
        
        task1 = EventTaskFactory(event=event, title='Book venue', priority='high')
        task2 = EventTaskFactory(event=event, title='Send invites', priority='medium')
        task3 = EventTaskFactory(event=event, title='Order catering', priority='medium')
        
        assert event.tasks.count() == 3
        assert event.tasks.filter(priority='high').count() == 1
        assert event.tasks.filter(priority='medium').count() == 2


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

@pytest.mark.django_db
class TestEventsIntegration:
    """Integration tests for event-related functionality"""
    
    def test_event_with_registrations_and_sponsors(self):
        """Test an event with both registrations and sponsors"""
        event = EventFactory(capacity=100)
        
        # Add registrations
        donors = [DonorFactory() for _ in range(10)]
        for donor in donors:
            EventRegistrationFactory(event=event, donor=donor)
        
        # Add sponsors
        sponsor1 = EventSponsorFactory(event=event, sponsorship_level='platinum')
        sponsor2 = EventSponsorFactory(event=event, sponsorship_level='gold')
        
        assert event.registrations.count() == 10
        assert event.sponsors.count() == 2
    
    def test_event_with_tasks_workflow(self):
        """Test event planning workflow with tasks"""
        event = EventFactory(status='planning')
        
        # Create planning tasks
        task1 = EventTaskFactory(event=event, title='Book venue', status='completed')
        task2 = EventTaskFactory(event=event, title='Send invitations', status='in_progress')
        task3 = EventTaskFactory(event=event, title='Confirm catering', status='pending')
        
        assert event.tasks.count() == 3
        assert event.tasks.filter(status='completed').count() == 1
        assert event.tasks.filter(status='in_progress').count() == 1
        assert event.tasks.filter(status='pending').count() == 1
    
    def test_event_capacity_management(self):
        """Test event capacity management with registrations"""
        event = EventFactory(capacity=50)
        
        # Register 45 attendees
        for _ in range(45):
            donor = DonorFactory()
            EventRegistrationFactory(event=event, donor=donor, status='confirmed')
        
        # Check remaining capacity
        remaining = event.capacity - event.registrations.filter(
            status__in=['registered', 'confirmed', 'attended']
        ).count()
        
        assert remaining == 5
    
    def test_donor_event_participation(self):
        """Test a donor participating in multiple events"""
        donor = DonorFactory()
        
        event1 = EventFactory(name='Spring Gala')
        event2 = EventFactory(name='Fall Auction')
        event3 = EventFactory(name='Holiday Party')
        
        reg1 = EventRegistrationFactory(event=event1, donor=donor, status='attended')
        reg2 = EventRegistrationFactory(event=event2, donor=donor, status='confirmed')
        reg3 = EventRegistrationFactory(event=event3, donor=donor, status='registered')
        
        assert donor.event_registrations.count() == 3
