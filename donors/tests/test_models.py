"""
Unit tests for Donors app.
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import models
from donors.models import Donor, DonorNote, DonorInteraction


class DonorModelTests(TestCase):
    """Test Donor model functionality."""
    
    def setUp(self):
        self.donor = Donor.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            phone="555-1234",
            donor_type=Donor.INDIVIDUAL,
            tags=["major_donor", "board_member"],
            total_donations=Decimal("1500.00"),
            donation_count=3
        )
    
    def test_donor_creation(self):
        """Test basic donor creation."""
        self.assertEqual(self.donor.first_name, "Jane")
        self.assertEqual(self.donor.last_name, "Smith")
        self.assertEqual(self.donor.email, "jane.smith@example.com")
        self.assertEqual(str(self.donor), "Jane Smith (jane.smith@example.com)")
    
    def test_donor_types(self):
        """Test donor type choices."""
        individual = Donor.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            donor_type=Donor.INDIVIDUAL
        )
        organization = Donor.objects.create(
            first_name="",
            last_name="",
            email="org@example.com",
            donor_type=Donor.ORGANIZATION,
            organization_name="Acme Corp"
        )
        foundation = Donor.objects.create(
            first_name="",
            last_name="",
            email="foundation@example.com",
            donor_type=Donor.FOUNDATION,
            organization_name="Smith Foundation"
        )
        
        self.assertEqual(individual.donor_type, "individual")
        self.assertEqual(organization.donor_type, "organization")
        self.assertEqual(foundation.donor_type, "foundation")
    
    def test_donor_tags(self):
        """Test donor tags functionality."""
        self.assertIn("major_donor", self.donor.tags)
        self.assertIn("board_member", self.donor.tags)
        
        # Test tag filtering (using JSON containment which works on most DBs)
        # For SQLite, we filter in Python since JSON contains isn't supported
        all_donors = Donor.objects.all()
        major_donors = [d for d in all_donors if "major_donor" in (d.tags or [])]
        self.assertIn(self.donor, major_donors)
    
    def test_donor_segments(self):
        """Test donor segments."""
        self.donor.segments = ["vip", "recurring"]
        self.donor.save()
        
        # For SQLite, filter in Python since JSON contains isn't supported
        all_donors = Donor.objects.all()
        vip_donors = [d for d in all_donors if "vip" in (d.segments or [])]
        self.assertIn(self.donor, vip_donors)
    
    def test_email_uniqueness(self):
        """Test that email must be unique."""
        with self.assertRaises(Exception):
            Donor.objects.create(
                first_name="Jane",
                last_name="Duplicate",
                email="jane.smith@example.com"  # Same email
            )
    
    def test_donor_stats_calculation(self):
        """Test donor statistics."""
        self.assertEqual(self.donor.total_donations, Decimal("1500.00"))
        self.assertEqual(self.donor.donation_count, 3)
        
        # Average donation
        avg = self.donor.total_donations / self.donor.donation_count
        self.assertEqual(avg, Decimal("500.00"))
    
    def test_full_name_property(self):
        """Test full name generation."""
        self.assertEqual(self.donor.full_name, "Jane Smith")
        
        # Organization donor
        org = Donor.objects.create(
            first_name="",
            last_name="",
            email="org@test.com",
            donor_type=Donor.ORGANIZATION,
            organization_name="Test Org"
        )
        self.assertEqual(org.full_name, "Test Org")
    
    def test_address_formatting(self):
        """Test address formatting."""
        self.donor.address_line1 = "123 Main St"
        self.donor.city = "New York"
        self.donor.state = "NY"
        self.donor.postal_code = "10001"
        self.donor.save()
        
        address = self.donor.formatted_address
        self.assertIn("123 Main St", address)
        self.assertIn("New York", address)
        self.assertIn("NY", address)


class DonorNoteTests(TestCase):
    """Test DonorNote model."""
    
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
    
    def test_note_creation(self):
        """Test creating a note."""
        note = DonorNote.objects.create(
            donor=self.donor,
            author=self.user,
            content="Met at gala event",
            note_type="interaction",
            is_private=False
        )
        
        self.assertEqual(note.donor, self.donor)
        self.assertEqual(note.author, self.user)
        self.assertEqual(note.content, "Met at gala event")
    
    def test_private_notes(self):
        """Test private note visibility."""
        public_note = DonorNote.objects.create(
            donor=self.donor,
            author=self.user,
            content="Public note",
            is_private=False
        )
        private_note = DonorNote.objects.create(
            donor=self.donor,
            author=self.user,
            content="Private note",
            is_private=True
        )
        
        public_notes = DonorNote.objects.filter(is_private=False)
        self.assertIn(public_note, public_notes)
        self.assertNotIn(private_note, public_notes)


class DonorInteractionTests(TestCase):
    """Test DonorInteraction model."""
    
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
    
    def test_interaction_creation(self):
        """Test creating an interaction."""
        interaction = DonorInteraction.objects.create(
            donor=self.donor,
            staff_member=self.user,
            interaction_type="phone_call",
            direction="outbound",
            subject="Thank you call",
            summary="Discussed upcoming campaign",
            outcome="positive"
        )
        
        self.assertEqual(interaction.donor, self.donor)
        self.assertEqual(interaction.interaction_type, "phone_call")
        self.assertEqual(interaction.outcome, "positive")
    
    def test_followup_required(self):
        """Test follow-up tracking."""
        interaction = DonorInteraction.objects.create(
            donor=self.donor,
            staff_member=self.user,
            interaction_type="meeting",
            requires_followup=True,
            followup_date=date.today() + timedelta(days=7)
        )
        
        self.assertTrue(interaction.requires_followup)
        self.assertIsNotNone(interaction.followup_date)
        
        # Test overdue followups
        overdue = DonorInteraction.objects.filter(
            requires_followup=True,
            followup_date__lt=date.today()
        )
        self.assertNotIn(interaction, overdue)  # Not overdue yet


class DonorAPITests(TestCase):
    """Test Donor API endpoints."""
    
    def setUp(self):
        self.client = Client()
        self.donor = Donor.objects.create(
            first_name="API",
            last_name="Test",
            email="api@test.com",
            donor_type=Donor.INDIVIDUAL
        )
    
    def test_list_donors(self):
        """Test GET /api/donors/."""
        response = self.client.get("/api/donors/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)
    
    def test_get_donor(self):
        """Test GET /api/donors/{id}/."""
        response = self.client.get(f"/api/donors/{self.donor.id}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["first_name"], "API")
        self.assertEqual(data["email"], "api@test.com")
    
    def test_create_donor(self):
        """Test POST /api/donors/."""
        payload = {
            "first_name": "New",
            "last_name": "Donor",
            "email": "new@example.com",
            "donor_type": "individual"
        }
        response = self.client.post(
            "/api/donors/",
            data=payload,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["first_name"], "New")
    
    def test_update_donor(self):
        """Test PUT /api/donors/{id}/."""
        payload = {
            "first_name": "Updated",
            "last_name": "Name"
        }
        response = self.client.put(
            f"/api/donors/{self.donor.id}/",
            data=payload,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        
        self.donor.refresh_from_db()
        self.assertEqual(self.donor.first_name, "Updated")
    
    def test_search_donors(self):
        """Test POST /api/donors/search."""
        payload = {"query": "API"}
        response = self.client.post(
            "/api/donors/search",
            data=payload,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    def test_donor_stats(self):
        """Test GET /api/donors/{id}/stats."""
        response = self.client.get(f"/api/donors/{self.donor.id}/stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_donations", data)
        self.assertIn("donation_count", data)


class DonorSearchTests(TestCase):
    """Test donor search functionality."""
    
    def setUp(self):
        self.donor1 = Donor.objects.create(
            first_name="Alice",
            last_name="Johnson",
            email="alice@example.com",
            tags=["major_donor"],
            total_donations=Decimal("5000.00")
        )
        self.donor2 = Donor.objects.create(
            first_name="Bob",
            last_name="Smith",
            email="bob@example.com",
            tags=["volunteer"],
            total_donations=Decimal("100.00")
        )
        self.donor3 = Donor.objects.create(
            first_name="Charlie",
            last_name="Brown",
            email="charlie@example.com",
            donor_type=Donor.ORGANIZATION,
            organization_name="Brown Corp",
            total_donations=Decimal("10000.00")
        )
    
    def test_search_by_name(self):
        """Test searching by name."""
        results = Donor.objects.filter(
            models.Q(first_name__icontains="Alice") |
            models.Q(last_name__icontains="Alice")
        )
        self.assertIn(self.donor1, results)
        self.assertNotIn(self.donor2, results)
    
    def test_search_by_email(self):
        """Test searching by email."""
        results = Donor.objects.filter(email__icontains="bob")
        self.assertIn(self.donor2, results)
        self.assertNotIn(self.donor1, results)
    
    def test_filter_by_tags(self):
        """Test filtering by tags."""
        # For SQLite, filter in Python since JSON contains isn't supported
        all_donors = Donor.objects.all()
        major_donors = [d for d in all_donors if "major_donor" in (d.tags or [])]
        self.assertIn(self.donor1, major_donors)
        self.assertNotIn(self.donor2, major_donors)
    
    def test_filter_by_donation_amount(self):
        """Test filtering by donation amount range."""
        high_donors = Donor.objects.filter(total_donations__gte=1000)
        self.assertIn(self.donor1, high_donors)
        self.assertIn(self.donor3, high_donors)
        self.assertNotIn(self.donor2, high_donors)
    
    def test_filter_by_donor_type(self):
        """Test filtering by donor type."""
        organizations = Donor.objects.filter(donor_type=Donor.ORGANIZATION)
        self.assertIn(self.donor3, organizations)
        self.assertNotIn(self.donor1, organizations)


class DonorEdgeCaseTests(TestCase):
    """Test edge cases and error handling."""
    
    def test_empty_name_handling(self):
        """Test handling of empty names."""
        donor = Donor.objects.create(
            first_name="",
            last_name="",
            email="empty@example.com",
            donor_type=Donor.ORGANIZATION,
            organization_name="Test Organization"
        )
        # __str__ returns "Organization Name (email)" for organizations
        self.assertEqual(str(donor), "Test Organization (empty@example.com)")
    
    def test_long_email(self):
        """Test handling of long email addresses."""
        long_email = "a" * 200 + "@example.com"
        # Django's EmailField validates on full_clean(), not on save()
        donor = Donor.objects.create(
            first_name="Test",
            last_name="User",
            email=long_email
        )
        # Verify the donor was created (Django doesn't validate on raw save)
        self.assertIsNotNone(donor.id)
        self.assertEqual(donor.email, long_email)
    
    def test_special_characters_in_names(self):
        """Test handling of special characters."""
        donor = Donor.objects.create(
            first_name="José",
            last_name="García-Müller",
            email="jose@example.com"
        )
        self.assertEqual(donor.first_name, "José")
        self.assertEqual(donor.last_name, "García-Müller")
    
    def test_unicode_tags(self):
        """Test unicode in tags."""
        donor = Donor.objects.create(
            first_name="Test",
            last_name="User",
            email="unicode@example.com",
            tags=["vip", "🌟", "日本語"]
        )
        self.assertIn("🌟", donor.tags)
        self.assertIn("日本語", donor.tags)



