"""
Unit tests for Communications app.
"""
import pytest
from datetime import datetime, date, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from donors.models import Donor
from communications.models import (
    Communication, CommunicationTemplate, CommunicationSchedule,
    CommunicationPreference
)


class CommunicationModelTests(TestCase):
    """Test Communication model functionality."""
    
    def setUp(self):
        self.donor = Donor.objects.create(
            first_name="Test",
            last_name="Donor",
            email="test@example.com"
        )
        self.user = User.objects.create_user(
            username="staff",
            password="testpass123"
        )
        self.communication = Communication.objects.create(
            donor=self.donor,
            communication_type=Communication.EMAIL,
            direction=Communication.OUTBOUND,
            subject="Thank you for your donation",
            content="Dear donor, thank you for your generous support...",
            from_address="staff@organization.org",
            to_address="test@example.com",
            status=Communication.SENT,
            sent_date=timezone.now()
        )
    
    def test_communication_creation(self):
        """Test basic communication creation."""
        self.assertEqual(self.communication.communication_type, Communication.EMAIL)
        self.assertEqual(self.communication.direction, Communication.OUTBOUND)
        self.assertEqual(self.communication.status, Communication.SENT)
    
    def test_communication_types(self):
        """Test different communication types."""
        types = [
            Communication.EMAIL,
            Communication.PHONE_CALL,
            Communication.MEETING,
            Communication.NOTE,
            Communication.LETTER,
            Communication.SMS,
            Communication.SOCIAL_MEDIA,
        ]
        
        for comm_type in types:
            comm = Communication.objects.create(
                donor=self.donor,
                communication_type=comm_type,
                direction=Communication.OUTBOUND,
                subject=f"{comm_type} test"
            )
            self.assertEqual(comm.communication_type, comm_type)
    
    def test_communication_directions(self):
        """Test inbound and outbound directions."""
        outbound = Communication.objects.create(
            donor=self.donor,
            communication_type=Communication.EMAIL,
            direction=Communication.OUTBOUND,
            subject="Outbound email"
        )
        
        inbound = Communication.objects.create(
            donor=self.donor,
            communication_type=Communication.EMAIL,
            direction=Communication.INBOUND,
            subject="Inbound email"
        )
        
        self.assertEqual(outbound.direction, Communication.OUTBOUND)
        self.assertEqual(inbound.direction, Communication.INBOUND)
    
    def test_communication_status_workflow(self):
        """Test communication status transitions."""
        comm = Communication.objects.create(
            donor=self.donor,
            communication_type=Communication.EMAIL,
            direction=Communication.OUTBOUND,
            status=Communication.DRAFT
        )
        
        comm.status = Communication.SCHEDULED
        comm.scheduled_date = timezone.now() + timedelta(hours=1)
        comm.save()
        self.assertEqual(comm.status, Communication.SCHEDULED)
        
        comm.status = Communication.SENT
        comm.sent_date = timezone.now()
        comm.save()
        self.assertEqual(comm.status, Communication.SENT)
        
        comm.status = Communication.DELIVERED
        comm.delivered_date = timezone.now()
        comm.save()
        self.assertEqual(comm.status, Communication.DELIVERED)
    
    def test_followup_tracking(self):
        """Test follow-up tracking."""
        comm = Communication.objects.create(
            donor=self.donor,
            communication_type=Communication.PHONE_CALL,
            direction=Communication.OUTBOUND,
            subject="Follow-up needed",
            requires_followup=True,
            followup_date=timezone.now() + timedelta(days=7)
        )
        
        self.assertTrue(comm.requires_followup)
        self.assertIsNotNone(comm.followup_date)
        
        # Mark followup complete
        comm.followup_completed = True
        comm.save()
        self.assertTrue(comm.followup_completed)
    
    def test_sentiment_tracking(self):
        """Test sentiment analysis tracking."""
        sentiments = ["positive", "neutral", "negative"]
        
        for sentiment in sentiments:
            comm = Communication.objects.create(
                donor=self.donor,
                communication_type=Communication.PHONE_CALL,
                sentiment=sentiment
            )
            self.assertEqual(comm.sentiment, sentiment)
    
    def test_thread_grouping(self):
        """Test communication threading."""
        thread_id = "thread_123"
        
        comm1 = Communication.objects.create(
            donor=self.donor,
            communication_type=Communication.EMAIL,
            thread_id=thread_id,
            subject="Original message"
        )
        
        comm2 = Communication.objects.create(
            donor=self.donor,
            communication_type=Communication.EMAIL,
            thread_id=thread_id,
            subject="Re: Original message"
        )
        
        thread_comms = Communication.objects.filter(thread_id=thread_id)
        self.assertEqual(thread_comms.count(), 2)


class CommunicationTemplateTests(TestCase):
    """Test CommunicationTemplate model."""
    
    def setUp(self):
        self.template = CommunicationTemplate.objects.create(
            name="Thank You Email",
            template_type=CommunicationTemplate.EMAIL,
            subject_template="Thank you, {{ donor.first_name }}!",
            body_template="Dear {{ donor.first_name }}, thank you for your ${{ donation.amount }} donation.",
            category="acknowledgment",
            is_active=True,
            available_variables=["donor.first_name", "donor.last_name", "donation.amount"]
        )
    
    def test_template_creation(self):
        """Test template creation."""
        self.assertEqual(self.template.name, "Thank You Email")
        self.assertEqual(self.template.template_type, CommunicationTemplate.EMAIL)
        self.assertTrue(self.template.is_active)
    
    def test_template_rendering(self):
        """Test template variable substitution."""
        donor = Donor.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com"
        )
        
        # Simulate rendering
        context = {
            "donor": {"first_name": "Jane", "last_name": "Smith"},
            "donation": {"amount": "100.00"}
        }
        
        subject = self.template.subject_template.replace(
            "{{ donor.first_name }}", context["donor"]["first_name"]
        )
        body = self.template.body_template.replace(
            "{{ donor.first_name }}", context["donor"]["first_name"]
        ).replace(
            "{{ donation.amount }}", context["donation"]["amount"]
        )
        
        self.assertEqual(subject, "Thank you, Jane!")
        self.assertIn("Jane", body)
        self.assertIn("100.00", body)
    
    def test_template_usage_count(self):
        """Test template usage tracking."""
        initial_count = self.template.usage_count
        
        # Simulate usage
        self.template.usage_count += 1
        self.template.save()
        
        self.assertEqual(self.template.usage_count, initial_count + 1)
    
    def test_template_categories(self):
        """Test template categorization."""
        categories = ["acknowledgment", "appeal", "newsletter", "reminder", "welcome"]
        
        for category in categories:
            template = CommunicationTemplate.objects.create(
                name=f"{category} template",
                template_type=CommunicationTemplate.EMAIL,
                body_template="Test content",
                category=category
            )
            self.assertEqual(template.category, category)


class CommunicationScheduleTests(TestCase):
    """Test CommunicationSchedule model."""
    
    def setUp(self):
        self.donor = Donor.objects.create(
            first_name="Scheduled",
            last_name="Donor",
            email="scheduled@example.com"
        )
        self.template = CommunicationTemplate.objects.create(
            name="Scheduled Email",
            template_type=CommunicationTemplate.EMAIL,
            body_template="Scheduled content"
        )
    
    def test_schedule_creation(self):
        """Test creating a scheduled communication."""
        schedule = CommunicationSchedule.objects.create(
            donor=self.donor,
            template=self.template,
            scheduled_date=timezone.now() + timedelta(days=1),
            subject="Scheduled subject",
            content="Scheduled content",
            status=CommunicationSchedule.PENDING
        )
        
        self.assertEqual(schedule.status, CommunicationSchedule.PENDING)
        self.assertIsNotNone(schedule.scheduled_date)
    
    def test_schedule_status_transitions(self):
        """Test schedule status workflow."""
        schedule = CommunicationSchedule.objects.create(
            donor=self.donor,
            scheduled_date=timezone.now() + timedelta(days=1),
            status=CommunicationSchedule.PENDING
        )
        
        schedule.status = CommunicationSchedule.PROCESSING
        schedule.save()
        self.assertEqual(schedule.status, CommunicationSchedule.PROCESSING)
        
        schedule.status = CommunicationSchedule.SENT
        schedule.sent_date = timezone.now()
        schedule.save()
        self.assertEqual(schedule.status, CommunicationSchedule.SENT)
    
    def test_overdue_schedules(self):
        """Test detecting overdue scheduled communications."""
        overdue = CommunicationSchedule.objects.create(
            donor=self.donor,
            scheduled_date=timezone.now() - timedelta(days=2),
            status=CommunicationSchedule.PENDING
        )
        
        upcoming = CommunicationSchedule.objects.create(
            donor=self.donor,
            scheduled_date=timezone.now() + timedelta(days=2),
            status=CommunicationSchedule.PENDING
        )
        
        overdue_schedules = CommunicationSchedule.objects.filter(
            scheduled_date__lt=timezone.now(),
            status=CommunicationSchedule.PENDING
        )
        
        self.assertIn(overdue, overdue_schedules)
        self.assertNotIn(upcoming, overdue_schedules)
    
    def test_automated_schedules(self):
        """Test automated schedule triggers."""
        schedule = CommunicationSchedule.objects.create(
            donor=self.donor,
            scheduled_date=timezone.now(),
            is_automated=True,
            automation_trigger="new_donation",
            status=CommunicationSchedule.PENDING
        )
        
        self.assertTrue(schedule.is_automated)
        self.assertEqual(schedule.automation_trigger, "new_donation")


class CommunicationPreferenceTests(TestCase):
    """Test CommunicationPreference model."""
    
    def setUp(self):
        self.donor = Donor.objects.create(
            first_name="Preference",
            last_name="Donor",
            email="pref@example.com"
        )
    
    def test_preference_creation(self):
        """Test creating communication preferences."""
        pref = CommunicationPreference.objects.create(
            donor=self.donor,
            email_opt_in=True,
            phone_opt_in=False,
            sms_opt_in=True,
            mail_opt_in=True,
            preferred_frequency=CommunicationPreference.MONTHLY,
            preferred_contact_time="morning",
            timezone="America/New_York"
        )
        
        self.assertTrue(pref.email_opt_in)
        self.assertFalse(pref.phone_opt_in)
        self.assertEqual(pref.preferred_frequency, CommunicationPreference.MONTHLY)
    
    def test_do_not_contact(self):
        """Test do not contact flag."""
        pref = CommunicationPreference.objects.create(
            donor=self.donor,
            do_not_contact=True,
            do_not_contact_reason="Requested by donor"
        )
        
        self.assertTrue(pref.do_not_contact)
        self.assertEqual(pref.do_not_contact_reason, "Requested by donor")
    
    def test_topic_preferences(self):
        """Test topic-based preferences."""
        pref = CommunicationPreference.objects.create(
            donor=self.donor,
            topics_of_interest=["education", "healthcare"],
            topics_to_exclude=["politics"]
        )
        
        self.assertIn("education", pref.topics_of_interest)
        self.assertIn("politics", pref.topics_to_exclude)


class CommunicationAPITests(TestCase):
    """Test Communication API endpoints."""
    
    def setUp(self):
        self.client = Client()
        self.donor = Donor.objects.create(
            first_name="API",
            last_name="Donor",
            email="api@example.com"
        )
        self.communication = Communication.objects.create(
            donor=self.donor,
            communication_type=Communication.EMAIL,
            direction=Communication.OUTBOUND,
            subject="API Test",
            content="Test content"
        )
    
    def test_list_communications(self):
        """Test GET /api/communications/."""
        response = self.client.get("/api/communications/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    def test_get_communication(self):
        """Test GET /api/communications/{id}/."""
        response = self.client.get(f"/api/communications/{self.communication.id}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["subject"], "API Test")
    
    def test_create_communication(self):
        """Test POST /api/communications/."""
        payload = {
            "donor_id": self.donor.id,
            "communication_type": "email",
            "direction": "outbound",
            "subject": "New communication",
            "content": "New content"
        }
        response = self.client.post(
            "/api/communications/",
            data=payload,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
    
    def test_list_templates(self):
        """Test GET /api/communications/templates."""
        response = self.client.get("/api/communications/templates")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    def test_followups(self):
        """Test GET /api/communications/followups."""
        response = self.client.get("/api/communications/followups")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)


class CommunicationEdgeCaseTests(TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        self.donor = Donor.objects.create(
            first_name="Edge",
            last_name="Case",
            email="edge@example.com"
        )
    
    def test_very_long_content(self):
        """Test handling of very long content."""
        long_content = "A" * 10000
        
        comm = Communication.objects.create(
            donor=self.donor,
            communication_type=Communication.NOTE,
            content=long_content
        )
        
        self.assertEqual(len(comm.content), 10000)
    
    def test_unicode_content(self):
        """Test unicode in communication content."""
        unicode_content = "Thank you! 🙏 Gracias! ありがとう!"
        
        comm = Communication.objects.create(
            donor=self.donor,
            communication_type=Communication.EMAIL,
            subject="Unicode test 🎉",
            content=unicode_content
        )
        
        self.assertEqual(comm.subject, "Unicode test 🎉")
        self.assertEqual(comm.content, unicode_content)
    
    def test_multiple_attachments(self):
        """Test handling multiple attachments."""
        attachments = [
            "https://example.com/file1.pdf",
            "https://example.com/file2.jpg",
            "https://example.com/file3.doc"
        ]
        
        comm = Communication.objects.create(
            donor=self.donor,
            communication_type=Communication.EMAIL,
            attachments=attachments
        )
        
        self.assertEqual(len(comm.attachments), 3)
    
    def test_scheduled_in_past(self):
        """Test scheduling communication in the past."""
        past_date = timezone.now() - timedelta(days=1)
        
        schedule = CommunicationSchedule.objects.create(
            donor=self.donor,
            scheduled_date=past_date,
            status=CommunicationSchedule.PENDING
        )
        
        # Should be flagged as overdue
        self.assertLess(schedule.scheduled_date, timezone.now())
