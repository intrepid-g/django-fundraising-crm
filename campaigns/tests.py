"""
Unit and API tests for Campaigns app.
"""
import pytest
import json
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from donors.models import Donor
from donations.models import Donation, Campaign


class CampaignAPITests(TestCase):
    """Test Campaign API endpoints."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='***'
        )
        self.client.force_login(self.user)
        
        # Create test campaigns
        self.active_campaign = Campaign.objects.create(
            name="Active Spring Campaign",
            description="Spring fundraising drive",
            goal_amount=Decimal("50000.00"),
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            is_active=True
        )
        
        self.inactive_campaign = Campaign.objects.create(
            name="Inactive Winter Campaign",
            description="Winter fundraising drive",
            goal_amount=Decimal("25000.00"),
            start_date=date.today() - timedelta(days=180),
            end_date=date.today() - timedelta(days=90),
            is_active=False
        )
    
    def test_list_campaigns(self):
        """Test listing all campaigns via API."""
        response = self.client.get('/api/campaigns/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        
        campaign_names = [c['name'] for c in data]
        self.assertIn("Active Spring Campaign", campaign_names)
        self.assertIn("Inactive Winter Campaign", campaign_names)
    
    def test_list_active_campaigns_only(self):
        """Test filtering to active campaigns only."""
        response = self.client.get('/api/campaigns/?active_only=true')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Active Spring Campaign")
        self.assertTrue(data[0]['is_active'])
    
    def test_get_campaign_detail(self):
        """Test retrieving a single campaign."""
        response = self.client.get(f'/api/campaigns/{self.active_campaign.id}/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['name'], "Active Spring Campaign")
        self.assertEqual(data['goal_amount'], "50000.00")
        self.assertEqual(data['description'], "Spring fundraising drive")
    
    def test_get_nonexistent_campaign(self):
        """Test retrieving a campaign that doesn't exist."""
        response = self.client.get('/api/campaigns/99999/')
        self.assertEqual(response.status_code, 404)
    
    def test_create_campaign(self):
        """Test creating a new campaign via API."""
        payload = {
            "name": "Summer 2024 Campaign",
            "description": "Summer fundraising initiative",
            "goal_amount": "75000.00",
            "start_date": str(date.today()),
            "end_date": str(date.today() + timedelta(days=60)),
            "is_active": True
        }
        
        response = self.client.post(
            '/api/campaigns/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['name'], "Summer 2024 Campaign")
        self.assertEqual(data['goal_amount'], "75000.00")
        
        # Verify campaign was created in database
        campaign = Campaign.objects.get(name="Summer 2024 Campaign")
        self.assertEqual(campaign.goal_amount, Decimal("75000.00"))
    
    def test_create_campaign_without_optional_fields(self):
        """Test creating a campaign with minimal required fields."""
        payload = {
            "name": "Minimal Campaign",
            "goal_amount": "10000.00",
            "start_date": str(date.today())
        }
        
        response = self.client.post(
            '/api/campaigns/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['name'], "Minimal Campaign")
        self.assertEqual(data['description'], "")  # Default empty string
        self.assertTrue(data['is_active'])  # Default True
    
    def test_create_campaign_invalid_data(self):
        """Test creating a campaign with invalid data."""
        payload = {
            "name": "",  # Empty name should be invalid
            "goal_amount": "-100.00",  # Negative amount
            "start_date": str(date.today())
        }
        
        response = self.client.post(
            '/api/campaigns/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        # API returns 422 for validation errors
        self.assertIn(response.status_code, [422, 400])
    
    def test_campaign_stats_endpoint(self):
        """Test campaign statistics endpoint."""
        # Create donor and donations for the campaign
        donor = Donor.objects.create(
            first_name="Test",
            last_name="Donor",
            email="donor@example.com"
        )
        
        Donation.objects.create(
            donor=donor,
            campaign=self.active_campaign,
            amount=Decimal("15000.00"),
            donation_date=date.today(),
            status=Donation.COMPLETED
        )
        
        Donation.objects.create(
            donor=donor,
            campaign=self.active_campaign,
            amount=Decimal("5000.00"),
            donation_date=date.today(),
            status=Donation.COMPLETED
        )
        
        response = self.client.get(f'/api/campaigns/{self.active_campaign.id}/stats/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['campaign_name'], "Active Spring Campaign")
        self.assertEqual(data['goal_amount'], 50000.0)
        self.assertEqual(data['total_raised'], 20000.0)
        self.assertEqual(data['donation_count'], 2)
        self.assertEqual(data['progress_percentage'], 40.0)
        self.assertIsNotNone(data['days_remaining'])
    
    def test_campaign_stats_no_donations(self):
        """Test campaign stats for campaign with no donations."""
        response = self.client.get(f'/api/campaigns/{self.inactive_campaign.id}/stats/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['total_raised'], 0.0)
        self.assertEqual(data['donation_count'], 0)
        self.assertEqual(data['progress_percentage'], 0.0)
    
    def test_campaign_stats_no_end_date(self):
        """Test campaign stats for campaign without end date."""
        campaign = Campaign.objects.create(
            name="Ongoing Campaign",
            goal_amount=Decimal("10000.00"),
            start_date=date.today(),
            end_date=None,
            is_active=True
        )
        
        response = self.client.get(f'/api/campaigns/{campaign.id}/stats/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIsNone(data['days_remaining'])


class CampaignStatsEdgeCaseTests(TestCase):
    """Test edge cases for campaign statistics."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='***'
        )
        self.client.force_login(self.user)
    
    def test_campaign_stats_zero_goal(self):
        """Test campaign stats with zero goal amount."""
        campaign = Campaign.objects.create(
            name="Zero Goal Campaign",
            goal_amount=Decimal("0.00"),
            start_date=date.today(),
            is_active=True
        )
        
        donor = Donor.objects.create(
            first_name="Test",
            last_name="Donor",
            email="test@example.com"
        )
        
        Donation.objects.create(
            donor=donor,
            campaign=campaign,
            amount=Decimal("100.00"),
            donation_date=date.today(),
            status=Donation.COMPLETED
        )
        
        response = self.client.get(f'/api/campaigns/{campaign.id}/stats/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        # Should not divide by zero
        self.assertEqual(data['progress_percentage'], 0.0)
    
    def test_campaign_stats_pending_donations_excluded(self):
        """Test that pending donations are not counted in stats."""
        campaign = Campaign.objects.create(
            name="Test Campaign",
            goal_amount=Decimal("10000.00"),
            start_date=date.today(),
            is_active=True
        )
        
        donor = Donor.objects.create(
            first_name="Test",
            last_name="Donor",
            email="test@example.com"
        )
        
        # Create a completed donation
        Donation.objects.create(
            donor=donor,
            campaign=campaign,
            amount=Decimal("5000.00"),
            donation_date=date.today(),
            status=Donation.COMPLETED
        )
        
        # Create a pending donation (should not count)
        Donation.objects.create(
            donor=donor,
            campaign=campaign,
            amount=Decimal("3000.00"),
            donation_date=date.today(),
            status=Donation.PENDING
        )
        
        response = self.client.get(f'/api/campaigns/{campaign.id}/stats/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        # Only completed donation should count
        self.assertEqual(data['total_raised'], 5000.0)
        self.assertEqual(data['donation_count'], 1)
    
    def test_campaign_stats_failed_donations_excluded(self):
        """Test that failed donations are not counted in stats."""
        campaign = Campaign.objects.create(
            name="Test Campaign",
            goal_amount=Decimal("10000.00"),
            start_date=date.today(),
            is_active=True
        )
        
        donor = Donor.objects.create(
            first_name="Test",
            last_name="Donor",
            email="test@example.com"
        )
        
        # Create a completed donation
        Donation.objects.create(
            donor=donor,
            campaign=campaign,
            amount=Decimal("5000.00"),
            donation_date=date.today(),
            status=Donation.COMPLETED
        )
        
        # Create failed and refunded donations (should not count)
        Donation.objects.create(
            donor=donor,
            campaign=campaign,
            amount=Decimal("2000.00"),
            donation_date=date.today(),
            status=Donation.FAILED
        )
        
        Donation.objects.create(
            donor=donor,
            campaign=campaign,
            amount=Decimal("1000.00"),
            donation_date=date.today(),
            status=Donation.REFUNDED
        )
        
        response = self.client.get(f'/api/campaigns/{campaign.id}/stats/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        # Only completed donation should count
        self.assertEqual(data['total_raised'], 5000.0)
        self.assertEqual(data['donation_count'], 1)


class CampaignOrderingTests(TestCase):
    """Test campaign ordering and filtering."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='***'
        )
        self.client.force_login(self.user)
    
    def test_campaigns_ordered_by_start_date_desc(self):
        """Test that campaigns are ordered by start date descending."""
        # Create campaigns with different start dates
        Campaign.objects.create(
            name="Oldest Campaign",
            goal_amount=Decimal("1000.00"),
            start_date=date.today() - timedelta(days=365),
            is_active=True
        )
        
        Campaign.objects.create(
            name="Newest Campaign",
            goal_amount=Decimal("2000.00"),
            start_date=date.today(),
            is_active=True
        )
        
        Campaign.objects.create(
            name="Middle Campaign",
            goal_amount=Decimal("1500.00"),
            start_date=date.today() - timedelta(days=180),
            is_active=True
        )
        
        response = self.client.get('/api/campaigns/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        names = [c['name'] for c in data]
        
        # Should be ordered by start_date descending (newest first)
        self.assertEqual(names[0], "Newest Campaign")
        self.assertEqual(names[1], "Middle Campaign")
        self.assertEqual(names[2], "Oldest Campaign")


class CampaignModelAPITests(TestCase):
    """Test Campaign model through API integration."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='***'
        )
        self.client.force_login(self.user)
    
    def test_campaign_date_validation_through_api(self):
        """Test that date validation works through API."""
        payload = {
            "name": "Invalid Date Campaign",
            "goal_amount": "1000.00",
            "start_date": str(date.today()),
            "end_date": str(date.today() - timedelta(days=1))  # End before start
        }
        
        response = self.client.post(
            '/api/campaigns/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Should fail validation - API returns 422 for validation errors
        self.assertIn(response.status_code, [422, 400])
    
    def test_campaign_decimal_precision(self):
        """Test that decimal amounts are handled correctly."""
        payload = {
            "name": "Precise Campaign",
            "goal_amount": "12345.67",
            "start_date": str(date.today())
        }
        
        response = self.client.post(
            '/api/campaigns/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['goal_amount'], "12345.67")
    
    def test_campaign_created_at_auto_set(self):
        """Test that created_at is automatically set."""
        payload = {
            "name": "Auto Timestamp Campaign",
            "goal_amount": "1000.00",
            "start_date": str(date.today())
        }
        
        response = self.client.post(
            '/api/campaigns/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIsNotNone(data['created_at'])
