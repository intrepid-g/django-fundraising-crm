"""
Unit tests for Donations app.
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from donors.models import Donor
from donations.models import Donation, Campaign, RecurringDonation


class CampaignModelTests(TestCase):
    """Test Campaign model functionality."""
    
    def setUp(self):
        self.campaign = Campaign.objects.create(
            name="Spring Fundraiser 2024",
            description="Annual spring fundraising campaign",
            goal_amount=Decimal("50000.00"),
            start_date=date(2024, 3, 1),
            end_date=date(2024, 5, 31),
            is_active=True
        )
    
    def test_campaign_creation(self):
        """Test basic campaign creation."""
        self.assertEqual(self.campaign.name, "Spring Fundraiser 2024")
        self.assertEqual(self.campaign.goal_amount, Decimal("50000.00"))
        self.assertTrue(self.campaign.is_active)
    
    def test_campaign_str(self):
        """Test campaign string representation."""
        self.assertEqual(str(self.campaign), "Spring Fundraiser 2024")
    
    def test_campaign_progress_calculation(self):
        """Test campaign progress calculation."""
        # Create donations
        donor = Donor.objects.create(
            first_name="Test",
            last_name="Donor",
            email="test@example.com"
        )
        
        Donation.objects.create(
            donor=donor,
            campaign=self.campaign,
            amount=Decimal("10000.00"),
            donation_date=date.today()
        )
        
        Donation.objects.create(
            donor=donor,
            campaign=self.campaign,
            amount=Decimal("5000.00"),
            donation_date=date.today()
        )
        
        # Calculate progress
        total = self.campaign.total_raised
        self.assertEqual(total, Decimal("15000.00"))
        
        percentage = (total / self.campaign.goal_amount) * 100
        self.assertEqual(percentage, Decimal("30.00"))
    
    def test_campaign_date_validation(self):
        """Test campaign date validation."""
        # End date before start date should be invalid
        with self.assertRaises(Exception):
            Campaign.objects.create(
                name="Invalid Campaign",
                goal_amount=Decimal("1000.00"),
                start_date=date(2024, 5, 1),
                end_date=date(2024, 3, 1)  # Before start
            )
    
    def test_campaign_active_filtering(self):
        """Test filtering active campaigns."""
        active = Campaign.objects.create(
            name="Active Campaign",
            goal_amount=Decimal("1000.00"),
            start_date=date.today(),
            is_active=True
        )
        inactive = Campaign.objects.create(
            name="Inactive Campaign",
            goal_amount=Decimal("1000.00"),
            start_date=date.today(),
            is_active=False
        )
        
        active_campaigns = Campaign.objects.filter(is_active=True)
        self.assertIn(active, active_campaigns)
        self.assertNotIn(inactive, active_campaigns)


class DonationModelTests(TestCase):
    """Test Donation model functionality."""
    
    def setUp(self):
        self.donor = Donor.objects.create(
            first_name="Test",
            last_name="Donor",
            email="test@example.com"
        )
        self.campaign = Campaign.objects.create(
            name="Test Campaign",
            goal_amount=Decimal("10000.00"),
            start_date=date.today()
        )
    
    def test_donation_creation(self):
        """Test basic donation creation."""
        donation = Donation.objects.create(
            donor=self.donor,
            campaign=self.campaign,
            amount=Decimal("100.00"),
            donation_type=Donation.ONE_TIME,
            donation_date=date.today(),
            status=Donation.COMPLETED
        )
        
        self.assertEqual(donation.amount, Decimal("100.00"))
        self.assertEqual(donation.donor, self.donor)
        self.assertEqual(donation.status, Donation.COMPLETED)
    
    def test_donation_types(self):
        """Test different donation types."""
        types = [
            (Donation.ONE_TIME, "One-time"),
            (Donation.RECURRING, "Recurring"),
            (Donation.IN_KIND, "In-kind"),
            (Donation.MATCHING, "Matching"),
            (Donation.STOCK, "Stock"),
            (Donation.LEGACY, "Legacy"),
        ]
        
        for donation_type, label in types:
            donation = Donation.objects.create(
                donor=self.donor,
                amount=Decimal("50.00"),
                donation_type=donation_type,
                donation_date=date.today()
            )
            self.assertEqual(donation.donation_type, donation_type)
    
    def test_donation_statuses(self):
        """Test donation status workflow."""
        donation = Donation.objects.create(
            donor=self.donor,
            amount=Decimal("100.00"),
            donation_date=date.today(),
            status=Donation.PENDING
        )
        
        # Status transitions
        donation.status = Donation.COMPLETED
        donation.save()
        self.assertEqual(donation.status, Donation.COMPLETED)
        
        donation.status = Donation.ACKNOWLEDGED
        donation.save()
        self.assertEqual(donation.status, Donation.ACKNOWLEDGED)
    
    def test_anonymous_donation(self):
        """Test anonymous donation flag."""
        donation = Donation.objects.create(
            donor=self.donor,
            amount=Decimal("500.00"),
            donation_date=date.today(),
            is_anonymous=True
        )
        
        self.assertTrue(donation.is_anonymous)
    
    def test_tribute_donation(self):
        """Test tribute/memorial donation."""
        donation = Donation.objects.create(
            donor=self.donor,
            amount=Decimal("200.00"),
            donation_date=date.today(),
            is_tribute=True,
            tribute_type="memory",
            tribute_honoree="Jane Smith",
            tribute_message="In loving memory"
        )
        
        self.assertTrue(donation.is_tribute)
        self.assertEqual(donation.tribute_honoree, "Jane Smith")
    
    def test_donation_acknowledgment(self):
        """Test donation acknowledgment tracking."""
        donation = Donation.objects.create(
            donor=self.donor,
            amount=Decimal("100.00"),
            donation_date=date.today(),
            status=Donation.COMPLETED
        )
        
        # Acknowledge
        donation.status = Donation.ACKNOWLEDGED
        donation.acknowledgment_date = date.today()
        donation.acknowledgment_method = "email"
        donation.save()
        
        self.assertEqual(donation.status, Donation.ACKNOWLEDGED)
        self.assertEqual(donation.acknowledgment_method, "email")
    
    def test_donation_updates_donor_stats(self):
        """Test that donations update donor statistics."""
        initial_total = self.donor.total_donations
        initial_count = self.donor.donation_count
        
        donation = Donation.objects.create(
            donor=self.donor,
            amount=Decimal("250.00"),
            donation_date=date.today(),
            status=Donation.COMPLETED
        )
        
        # Refresh donor
        self.donor.refresh_from_db()
        
        self.assertEqual(
            self.donor.total_donations,
            initial_total + Decimal("250.00")
        )
        self.assertEqual(self.donor.donation_count, initial_count + 1)
        self.assertEqual(self.donor.last_donation_date, date.today())


class RecurringDonationTests(TestCase):
    """Test RecurringDonation model."""
    
    def setUp(self):
        self.donor = Donor.objects.create(
            first_name="Recurring",
            last_name="Donor",
            email="recurring@example.com"
        )
    
    def test_recurring_donation_creation(self):
        """Test creating a recurring donation."""
        recurring = RecurringDonation.objects.create(
            donor=self.donor,
            amount=Decimal("50.00"),
            frequency=RecurringDonation.MONTHLY,
            start_date=date.today(),
            status=RecurringDonation.ACTIVE
        )
        
        self.assertEqual(recurring.amount, Decimal("50.00"))
        self.assertEqual(recurring.frequency, RecurringDonation.MONTHLY)
        self.assertEqual(recurring.status, RecurringDonation.ACTIVE)
    
    def test_recurring_frequencies(self):
        """Test different recurring frequencies."""
        frequencies = [
            RecurringDonation.WEEKLY,
            RecurringDonation.BIWEEKLY,
            RecurringDonation.MONTHLY,
            RecurringDonation.QUARTERLY,
            RecurringDonation.ANNUALLY,
        ]
        
        for freq in frequencies:
            recurring = RecurringDonation.objects.create(
                donor=self.donor,
                amount=Decimal("100.00"),
                frequency=freq,
                start_date=date.today()
            )
            self.assertEqual(recurring.frequency, freq)
    
    def test_recurring_status_changes(self):
        """Test recurring donation status changes."""
        recurring = RecurringDonation.objects.create(
            donor=self.donor,
            amount=Decimal("25.00"),
            frequency=RecurringDonation.MONTHLY,
            start_date=date.today(),
            status=RecurringDonation.ACTIVE
        )
        
        # Pause
        recurring.status = RecurringDonation.PAUSED
        recurring.save()
        self.assertEqual(recurring.status, RecurringDonation.PAUSED)
        
        # Cancel
        recurring.status = RecurringDonation.CANCELLED
        recurring.cancelled_date = date.today()
        recurring.cancellation_reason = "Financial constraints"
        recurring.save()
        
        self.assertEqual(recurring.status, RecurringDonation.CANCELLED)
        self.assertEqual(recurring.cancellation_reason, "Financial constraints")
    
    def test_next_payment_date_calculation(self):
        """Test next payment date calculation."""
        recurring = RecurringDonation.objects.create(
            donor=self.donor,
            amount=Decimal("100.00"),
            frequency=RecurringDonation.MONTHLY,
            start_date=date(2024, 1, 15),
            status=RecurringDonation.ACTIVE
        )
        
        # Next payment should be Feb 15
        next_date = recurring.calculate_next_payment_date()
        self.assertEqual(next_date, date(2024, 2, 15))


class DonationAPITests(TestCase):
    """Test Donation API endpoints."""
    
    def setUp(self):
        self.client = Client()
        self.donor = Donor.objects.create(
            first_name="API",
            last_name="Donor",
            email="api@example.com"
        )
        self.campaign = Campaign.objects.create(
            name="API Campaign",
            goal_amount=Decimal("10000.00"),
            start_date=date.today()
        )
        self.donation = Donation.objects.create(
            donor=self.donor,
            campaign=self.campaign,
            amount=Decimal("150.00"),
            donation_date=date.today()
        )
    
    def test_list_donations(self):
        """Test GET /api/donations/."""
        response = self.client.get("/api/donations/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    def test_get_donation(self):
        """Test GET /api/donations/{id}/."""
        response = self.client.get(f"/api/donations/{self.donation.id}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(Decimal(data["amount"]), Decimal("150.00"))
    
    def test_create_donation(self):
        """Test POST /api/donations/."""
        payload = {
            "donor_id": self.donor.id,
            "campaign_id": self.campaign.id,
            "amount": "200.00",
            "donation_type": "one_time",
            "donation_date": str(date.today())
        }
        response = self.client.post(
            "/api/donations/",
            data=payload,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
    
    def test_list_campaigns(self):
        """Test GET /api/campaigns/."""
        response = self.client.get("/api/campaigns/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    def test_get_campaign(self):
        """Test GET /api/campaigns/{id}/."""
        response = self.client.get(f"/api/campaigns/{self.campaign.id}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "API Campaign")
    
    def test_create_campaign(self):
        """Test POST /api/campaigns/."""
        payload = {
            "name": "New Campaign",
            "goal_amount": "5000.00",
            "start_date": str(date.today()),
            "is_active": True
        }
        response = self.client.post(
            "/api/campaigns/",
            data=payload,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
    
    def test_donation_summary(self):
        """Test GET /api/donations/summary."""
        response = self.client.get("/api/donations/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_amount", data)
        self.assertIn("total_count", data)


class DonationAggregationTests(TestCase):
    """Test donation aggregation and reporting."""
    
    def setUp(self):
        self.donor1 = Donor.objects.create(
            first_name="Donor1",
            last_name="Test",
            email="donor1@example.com"
        )
        self.donor2 = Donor.objects.create(
            first_name="Donor2",
            last_name="Test",
            email="donor2@example.com"
        )
        
        # Create donations across different dates
        Donation.objects.create(
            donor=self.donor1,
            amount=Decimal("100.00"),
            donation_date=date(2024, 1, 15)
        )
        Donation.objects.create(
            donor=self.donor1,
            amount=Decimal("200.00"),
            donation_date=date(2024, 2, 15)
        )
        Donation.objects.create(
            donor=self.donor2,
            amount=Decimal("150.00"),
            donation_date=date(2024, 1, 20)
        )
    
    def test_total_donations_by_month(self):
        """Test aggregating donations by month."""
        from django.db.models import Sum
        from django.db.models.functions import TruncMonth
        
        monthly_totals = Donation.objects.annotate(
            month=TruncMonth('donation_date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        self.assertTrue(len(monthly_totals) > 0)
    
    def test_average_donation_calculation(self):
        """Test calculating average donation amount."""
        from django.db.models import Avg
        
        avg = Donation.objects.aggregate(avg_amount=Avg('amount'))
        self.assertIsNotNone(avg['avg_amount'])
        # (100 + 200 + 150) / 3 = 150
        self.assertEqual(avg['avg_amount'], Decimal("150.00"))
    
    def test_donor_lifetime_value(self):
        """Test calculating donor lifetime value."""
        donor1_total = Donation.objects.filter(
            donor=self.donor1
        ).aggregate(total=Sum('amount'))['total']
        
        self.assertEqual(donor1_total, Decimal("300.00"))


class DonationEdgeCaseTests(TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        self.donor = Donor.objects.create(
            first_name="Test",
            last_name="Donor",
            email="test@example.com"
        )
    
    def test_zero_amount_donation(self):
        """Test handling of zero amount donations."""
        with self.assertRaises(Exception):
            Donation.objects.create(
                donor=self.donor,
                amount=Decimal("0.00"),
                donation_date=date.today()
            )
    
    def test_negative_amount_donation(self):
        """Test handling of negative amount donations."""
        with self.assertRaises(Exception):
            Donation.objects.create(
                donor=self.donor,
                amount=Decimal("-50.00"),
                donation_date=date.today()
            )
    
    def test_very_large_donation(self):
        """Test handling of very large donations."""
        donation = Donation.objects.create(
            donor=self.donor,
            amount=Decimal("999999999.99"),
            donation_date=date.today()
        )
        self.assertEqual(donation.amount, Decimal("999999999.99"))
    
    def test_future_donation_date(self):
        """Test handling of future donation dates."""
        future_date = date.today() + timedelta(days=30)
        donation = Donation.objects.create(
            donor=self.donor,
            amount=Decimal("100.00"),
            donation_date=future_date,
            status=Donation.PENDING
        )
        self.assertEqual(donation.donation_date, future_date)


# Import required for aggregation tests
from django.db.models import Sum, Avg
from django.db.models.functions import TruncMonth
