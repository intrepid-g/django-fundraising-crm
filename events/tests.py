"""
Unit tests for Events app.
"""
import pytest
from decimal import Decimal
from datetime import datetime, date, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from donors.models import Donor
from events.models import Event, EventRegistration, EventSponsor, EventTask


class EventModelTests(TestCase):
    """Test Event model functionality."""
    
    def setUp(self):
        self.event = Event.objects.create(
            name="Annual Gala 2024",
            description="Our biggest fundraising event of the year",
            event_type=Event.GALA,
            status=Event.CONFIRMED,
            start_date=timezone.make_aware(datetime(2024, 6, 15, 18, 0)),
            end_date=timezone.make_aware(datetime(2024, 6, 15, 23, 0)),
            venue_name="Grand Ballroom",
            venue_address="123 Main St",
            venue_city="New York",
            venue_state="NY",
            capacity=200,
            fundraising_goal=Decimal("100000.00"),
            ticket_price=Decimal("250.00")
        )
    
    def test_event_creation(self):
        """Test basic event creation."""
        self.assertEqual(self.event.name, "Annual Gala 2024")
        self.assertEqual(self.event.event_type, Event.GALA)
        self.assertEqual(self.event.status, Event.CONFIRMED)
    
    def test_event_types(self):
        """Test different event types."""
        types = [
            (Event.GALA, "Gala"),
            (Event.DINNER, "Dinner"),
            (Event.AUCTION, "Auction"),
            (Event.GOLF_TOURNAMENT, "Golf Tournament"),
            (Event.WALKATHON, "Walkathon"),
            (Event.CONCERT, "Concert"),
            (Event.MEETING, "Meeting"),
            (Event.OTHER, "Other"),
        ]
        
        for event_type, label in types:
            event = Event.objects.create(
                name=f"{label} Test",
                event_type=event_type,
                start_date=timezone.now()
            )
            self.assertEqual(event.event_type, event_type)
    
    def test_event_status_workflow(self):
        """Test event status transitions."""
        event = Event.objects.create(
            name="Draft Event",
            event_type=Event.MEETING,
            status=Event.DRAFT,
            start_date=timezone.now()
        )
        
        # Transition through statuses
        event.status = Event.PLANNING
        event.save()
        self.assertEqual(event.status, Event.PLANNING)
        
        event.status = Event.CONFIRMED
        event.save()
        self.assertEqual(event.status, Event.CONFIRMED)
    
    def test_virtual_event(self):
        """Test virtual event creation."""
        virtual_event = Event.objects.create(
            name="Virtual Fundraiser",
            event_type=Event.MEETING,
            status=Event.CONFIRMED,
            start_date=timezone.now(),
            is_virtual=True,
            virtual_event_url="https://zoom.us/j/123456"
        )
        
        self.assertTrue(virtual_event.is_virtual)
        self.assertEqual(virtual_event.virtual_event_url, "https://zoom.us/j/123456")
    
    def test_event_capacity(self):
        """Test event capacity management."""
        self.assertEqual(self.event.capacity, 200)
        
        # Create registrations
        donor1 = Donor.objects.create(
            first_name="Attendee1", last_name="Test", email="a1@example.com"
        )
        donor2 = Donor.objects.create(
            first_name="Attendee2", last_name="Test", email="a2@example.com"
        )
        
        EventRegistration.objects.create(
            event=self.event,
            donor=donor1,
            number_of_guests=2,
            status=EventRegistration.CONFIRMED
        )
        EventRegistration.objects.create(
            event=self.event,
            donor=donor2,
            number_of_guests=3,
            status=EventRegistration.CONFIRMED
        )
        
        # Calculate total attendees
        total = sum(
            reg.number_of_guests 
            for reg in EventRegistration.objects.filter(
                event=self.event,
                status=EventRegistration.CONFIRMED
            )
        )
        self.assertEqual(total, 5)
    
    def test_event_fundraising_progress(self):
        """Test event fundraising tracking."""
        self.event.total_raised = Decimal("50000.00")
        self.event.save()
        
        percentage = (self.event.total_raised / self.event.fundraising_goal) * 100
        self.assertEqual(percentage, Decimal("50.00"))
    
    def test_event_date_validation(self):
        """Test event date validation."""
        # End date before start date
        with self.assertRaises(Exception):
            Event.objects.create(
                name="Invalid Event",
                event_type=Event.MEETING,
                start_date=timezone.make_aware(datetime(2024, 6, 15, 18, 0)),
                end_date=timezone.make_aware(datetime(2024, 6, 15, 16, 0))  # Before start
            )


class EventRegistrationTests(TestCase):
    """Test EventRegistration model."""
    
    def setUp(self):
        self.event = Event.objects.create(
            name="Test Event",
            event_type=Event.GALA,
            start_date=timezone.now()
        )
        self.donor = Donor.objects.create(
            first_name="Test",
            last_name="Attendee",
            email="attendee@example.com"
        )
    
    def test_registration_creation(self):
        """Test creating an event registration."""
        registration = EventRegistration.objects.create(
            event=self.event,
            donor=self.donor,
            number_of_guests=2,
            dietary_requirements="Vegetarian",
            status=EventRegistration.CONFIRMED,
            amount_paid=Decimal("500.00")
        )
        
        self.assertEqual(registration.event, self.event)
        self.assertEqual(registration.donor, self.donor)
        self.assertEqual(registration.number_of_guests, 2)
    
    def test_registration_statuses(self):
        """Test registration status workflow."""
        registration = EventRegistration.objects.create(
            event=self.event,
            donor=self.donor,
            status=EventRegistration.PENDING
        )
        
        registration.status = EventRegistration.CONFIRMED
        registration.save()
        self.assertEqual(registration.status, EventRegistration.CONFIRMED)
        
        registration.status = EventRegistration.CANCELLED
        registration.cancellation_date = date.today()
        registration.cancellation_reason = "Unable to attend"
        registration.save()
        
        self.assertEqual(registration.status, EventRegistration.CANCELLED)
    
    def test_check_in(self):
        """Test attendee check-in."""
        registration = EventRegistration.objects.create(
            event=self.event,
            donor=self.donor,
            status=EventRegistration.CONFIRMED
        )
        
        # Check in
        registration.checked_in_at = timezone.now()
        registration.save()
        
        self.assertIsNotNone(registration.checked_in_at)
    
    def test_waitlist_management(self):
        """Test waitlist functionality."""
        # Fill capacity
        self.event.capacity = 1
        self.event.save()
        
        # First registration confirmed
        donor1 = Donor.objects.create(
            first_name="First", last_name="User", email="first@example.com"
        )
        EventRegistration.objects.create(
            event=self.event,
            donor=donor1,
            status=EventRegistration.CONFIRMED
        )
        
        # Second registration waitlisted
        registration = EventRegistration.objects.create(
            event=self.event,
            donor=self.donor,
            status=EventRegistration.WAITLISTED,
            waitlist_position=1
        )
        
        self.assertEqual(registration.status, EventRegistration.WAITLISTED)
        self.assertEqual(registration.waitlist_position, 1)


class EventSponsorTests(TestCase):
    """Test EventSponsor model."""
    
    def setUp(self):
        self.event = Event.objects.create(
            name="Sponsored Event",
            event_type=Event.GALA,
            start_date=timezone.now(),
            sponsor_goal=Decimal("50000.00")
        )
        self.sponsor_donor = Donor.objects.create(
            first_name="Corporate",
            last_name="Sponsor",
            email="sponsor@example.com",
            donor_type=Donor.ORGANIZATION,
            organization_name="Big Corp Inc"
        )
    
    def test_sponsor_creation(self):
        """Test creating an event sponsor."""
        sponsor = EventSponsor.objects.create(
            event=self.event,
            donor=self.sponsor_donor,
            sponsor_level=EventSponsor.PLATINUM,
            amount_pledged=Decimal("25000.00"),
            amount_paid=Decimal("12500.00"),
            status=EventSponsor.CONFIRMED,
            benefits_provided=["Logo on banner", "VIP table"]
        )
        
        self.assertEqual(sponsor.sponsor_level, EventSponsor.PLATINUM)
        self.assertEqual(sponsor.amount_pledged, Decimal("25000.00"))
    
    def test_sponsor_levels(self):
        """Test different sponsor levels."""
        levels = [
            EventSponsor.PLATINUM,
            EventSponsor.GOLD,
            EventSponsor.SILVER,
            EventSponsor.BRONZE,
        ]
        
        for i, level in enumerate(levels):
            donor = Donor.objects.create(
                first_name=f"Sponsor{i}",
                last_name="Test",
                email=f"sponsor{i}@example.com"
            )
            sponsor = EventSponsor.objects.create(
                event=self.event,
                donor=donor,
                sponsor_level=level,
                amount_pledged=Decimal("1000.00")
            )
            self.assertEqual(sponsor.sponsor_level, level)
    
    def test_sponsor_progress(self):
        """Test sponsor goal progress."""
        EventSponsor.objects.create(
            event=self.event,
            donor=self.sponsor_donor,
            sponsor_level=EventSponsor.GOLD,
            amount_pledged=Decimal("15000.00"),
            amount_paid=Decimal("15000.00"),
            status=EventSponsor.CONFIRMED
        )
        
        # Add another sponsor
        donor2 = Donor.objects.create(
            first_name="Another", last_name="Sponsor", email="another@example.com"
        )
        EventSponsor.objects.create(
            event=self.event,
            donor=donor2,
            sponsor_level=EventSponsor.SILVER,
            amount_pledged=Decimal("10000.00"),
            amount_paid=Decimal("10000.00"),
            status=EventSponsor.CONFIRMED
        )
        
        total = sum(
            s.amount_pledged 
            for s in EventSponsor.objects.filter(
                event=self.event,
                status=EventSponsor.CONFIRMED
            )
        )
        
        self.assertEqual(total, Decimal("25000.00"))
        percentage = (total / self.event.sponsor_goal) * 100
        self.assertEqual(percentage, Decimal("50.00"))


class EventTaskTests(TestCase):
    """Test EventTask model."""
    
    def setUp(self):
        self.event = Event.objects.create(
            name="Task Event",
            event_type=Event.GALA,
            start_date=timezone.now()
        )
        self.user = User.objects.create_user(
            username="event_manager",
            password="testpass123"
        )
    
    def test_task_creation(self):
        """Test creating an event task."""
        task = EventTask.objects.create(
            event=self.event,
            title="Book venue",
            description="Contact Grand Ballroom for June 15",
            assigned_to=self.user,
            due_date=date.today() + timedelta(days=30),
            priority=EventTask.HIGH,
            status=EventTask.PENDING
        )
        
        self.assertEqual(task.title, "Book venue")
        self.assertEqual(task.priority, EventTask.HIGH)
    
    def test_task_priorities(self):
        """Test task priority levels."""
        priorities = [
            EventTask.LOW,
            EventTask.MEDIUM,
            EventTask.HIGH,
            EventTask.URGENT,
        ]
        
        for priority in priorities:
            task = EventTask.objects.create(
                event=self.event,
                title=f"{priority} task",
                priority=priority
            )
            self.assertEqual(task.priority, priority)
    
    def test_task_completion(self):
        """Test task completion workflow."""
        task = EventTask.objects.create(
            event=self.event,
            title="Send invitations",
            status=EventTask.PENDING
        )
        
        task.status = EventTask.IN_PROGRESS
        task.save()
        self.assertEqual(task.status, EventTask.IN_PROGRESS)
        
        task.status = EventTask.COMPLETED
        task.completed_at = timezone.now()
        task.completed_by = self.user
        task.save()
        
        self.assertEqual(task.status, EventTask.COMPLETED)
        self.assertIsNotNone(task.completed_at)
    
    def test_overdue_tasks(self):
        """Test overdue task detection."""
        overdue_task = EventTask.objects.create(
            event=self.event,
            title="Overdue task",
            due_date=date.today() - timedelta(days=5),
            status=EventTask.PENDING
        )
        
        on_time_task = EventTask.objects.create(
            event=self.event,
            title="On time task",
            due_date=date.today() + timedelta(days=5),
            status=EventTask.PENDING
        )
        
        overdue = EventTask.objects.filter(
            due_date__lt=date.today(),
            status__in=[EventTask.PENDING, EventTask.IN_PROGRESS]
        )
        
        self.assertIn(overdue_task, overdue)
        self.assertNotIn(on_time_task, overdue)


class EventAPITests(TestCase):
    """Test Event API endpoints."""
    
    def setUp(self):
        self.client = Client()
        self.event = Event.objects.create(
            name="API Event",
            event_type=Event.GALA,
            status=Event.CONFIRMED,
            start_date=timezone.now()
        )
        self.donor = Donor.objects.create(
            first_name="Event",
            last_name="Attendee",
            email="event@example.com"
        )
    
    def test_list_events(self):
        """Test GET /api/events/."""
        response = self.client.get("/api/events/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    def test_get_event(self):
        """Test GET /api/events/{id}/."""
        response = self.client.get(f"/api/events/{self.event.id}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "API Event")
    
    def test_create_event(self):
        """Test POST /api/events/."""
        payload = {
            "name": "New Event",
            "event_type": "dinner",
            "status": "draft",
            "start_date": timezone.now().isoformat()
        }
        response = self.client.post(
            "/api/events/",
            data=payload,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
    
    def test_list_registrations(self):
        """Test GET /api/events/{id}/registrations."""
        response = self.client.get(f"/api/events/{self.event.id}/registrations")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    def test_create_registration(self):
        """Test POST /api/events/{id}/registrations."""
        payload = {
            "donor_id": self.donor.id,
            "number_of_guests": 2,
            "amount_paid": "500.00"
        }
        response = self.client.post(
            f"/api/events/{self.event.id}/registrations",
            data=payload,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
    
    def test_upcoming_events(self):
        """Test GET /api/events/upcoming."""
        response = self.client.get("/api/events/upcoming")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    def test_event_stats(self):
        """Test GET /api/events/{id}/stats."""
        response = self.client.get(f"/api/events/{self.event.id}/stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_registrations", data)
        self.assertIn("total_raised", data)


class EventEdgeCaseTests(TestCase):
    """Test edge cases and error handling."""
    
    def test_past_event_creation(self):
        """Test creating an event in the past."""
        past_date = timezone.now() - timedelta(days=365)
        event = Event.objects.create(
            name="Past Event",
            event_type=Event.MEETING,
            start_date=past_date,
            status=Event.COMPLETED
        )
        self.assertEqual(event.status, Event.COMPLETED)
    
    def test_zero_capacity_event(self):
        """Test event with zero capacity."""
        with self.assertRaises(Exception):
            Event.objects.create(
                name="Invalid Event",
                event_type=Event.GALA,
                start_date=timezone.now(),
                capacity=0
            )
    
    def test_very_long_event(self):
        """Test multi-day event."""
        start = timezone.make_aware(datetime(2024, 6, 15, 9, 0))
        end = timezone.make_aware(datetime(2024, 6, 17, 17, 0))
        
        event = Event.objects.create(
            name="Conference",
            event_type=Event.MEETING,
            start_date=start,
            end_date=end
        )
        
        duration = event.end_date - event.start_date
        self.assertEqual(duration.days, 2)
    
    def test_registration_without_capacity(self):
        """Test registration when at capacity."""
        event = Event.objects.create(
            name="Full Event",
            event_type=Event.GALA,
            start_date=timezone.now(),
            capacity=1
        )
        
        donor1 = Donor.objects.create(
            first_name="First", last_name="User", email="first@example.com"
        )
        donor2 = Donor.objects.create(
            first_name="Second", last_name="User", email="second@example.com"
        )
        
        # First registration
        EventRegistration.objects.create(
            event=event,
            donor=donor1,
            status=EventRegistration.CONFIRMED
        )
        
        # Second should be waitlisted
        registration = EventRegistration.objects.create(
            event=event,
            donor=donor2,
            status=EventRegistration.WAITLISTED,
            waitlist_position=1
        )
        
        self.assertEqual(registration.status, EventRegistration.WAITLISTED)
