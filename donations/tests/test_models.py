"""
Donations app model tests
Comprehensive unit tests for all donation-related models
"""
import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from donations.models import Donation, RecurringDonation
from factories import DonorFactory, DonationFactory, RecurringDonationFactory


@pytest.mark.django_db
class TestDonationModel:
    """Test cases for the Donation model"""
    
    def test_create_donation_with_valid_data(self):
        """Test creating a donation with valid data"""
        donor = DonorFactory()
        donation = DonationFactory(donor=donor, amount=Decimal('100.00'))
        
        assert donation.id is not None
        assert donation.donor == donor
        assert donation.amount == Decimal('100.00')
    
    def test_donation_str_representation(self):
        """Test the string representation of a donation"""
        donor = DonorFactory(first_name='John', last_name='Doe')
        donation = DonationFactory(donor=donor, amount=Decimal('50.00'))
        
        str_repr = str(donation)
        assert 'John Doe' in str_repr or 'Doe' in str_repr
        assert '50.00' in str_repr or '50' in str_repr
    
    def test_donation_amount_must_be_positive(self):
        """Test that donation amount must be positive"""
        donor = DonorFactory()
        
        with pytest.raises(Exception):
            DonationFactory(donor=donor, amount=Decimal('-10.00'))
    
    def test_donation_donor_required(self):
        """Test that donation requires a donor"""
        with pytest.raises(Exception):
            Donation.objects.create(amount=Decimal('100.00'))
    
    def test_donation_status_choices(self):
        """Test donation status choices"""
        donor = DonorFactory()
        
        for status in ['pending', 'completed', 'failed', 'refunded']:
            donation = DonationFactory(donor=donor, status=status)
            assert donation.status == status
    
    def test_donation_payment_method_choices(self):
        """Test payment method choices"""
        donor = DonorFactory()
        
        for method in ['credit_card', 'bank_transfer', 'check', 'cash', 'crypto']:
            donation = DonationFactory(donor=donor, payment_method=method)
            assert donation.payment_method == method
    
    def test_donation_currency_default(self):
        """Test default currency is USD"""
        donor = DonorFactory()
        donation = DonationFactory(donor=donor)
        
        assert donation.currency == 'USD'
    
    def test_donation_receipt_tracking(self):
        """Test donation receipt tracking fields"""
        donor = DonorFactory()
        donation = DonationFactory(
            donor=donor,
            receipt_sent=True
        )
        
        assert donation.receipt_sent is True
    
    def test_donation_campaign_tracking(self):
        """Test donation campaign and event tracking"""
        donor = DonorFactory()
        donation = DonationFactory(
            donor=donor,
            campaign='Spring2024'
        )
        
        assert donation.campaign == 'Spring2024'
    
    def test_donation_transaction_id(self):
        """Test donation transaction ID field"""
        donor = DonorFactory()
        donation = DonationFactory(donor=donor, transaction_id='txn_12345')
        
        assert donation.transaction_id == 'txn_12345'
    
    def test_donation_notes_field(self):
        """Test donation notes field"""
        donor = DonorFactory()
        donation = DonationFactory(donor=donor, notes='Special donation')
        
        assert donation.notes == 'Special donation'
    
    def test_donation_timestamps(self):
        """Test donation timestamps"""
        donor = DonorFactory()
        donation = DonationFactory(donor=donor)
        
        assert donation.donation_date is not None
        assert donation.created_at is not None
    
    def test_donation_update_fields(self):
        """Test updating donation fields"""
        donor = DonorFactory()
        donation = DonationFactory(donor=donor, amount=Decimal('50.00'), status='pending')
        
        donation.amount = Decimal('75.00')
        donation.status = 'completed'
        donation.save()
        
        updated_donation = Donation.objects.get(id=donation.id)
        assert updated_donation.amount == Decimal('75.00')
        assert updated_donation.status == 'completed'
    
    def test_donation_cascade_delete(self):
        """Test that donations are deleted when donor is deleted"""
        donor = DonorFactory()
        donation = DonationFactory(donor=donor)
        donation_id = donation.id
        
        donor.delete()
        
        with pytest.raises(Donation.DoesNotExist):
            Donation.objects.get(id=donation_id)
    
    def test_donation_decimal_precision(self):
        """Test donation amount decimal precision"""
        donor = DonorFactory()
        donation = DonationFactory(donor=donor, amount=Decimal('123.45'))
        
        assert donation.amount == Decimal('123.45')


@pytest.mark.django_db
class TestRecurringDonationModel:
    """Test cases for the RecurringDonation model"""
    
    def test_create_recurring_donation_with_valid_data(self):
        """Test creating a recurring donation with valid data"""
        donor = DonorFactory()
        recurring = RecurringDonationFactory(
            donor=donor,
            amount=Decimal('25.00'),
            frequency='monthly'
        )
        
        assert recurring.id is not None
        assert recurring.donor == donor
        assert recurring.amount == Decimal('25.00')
        assert recurring.frequency == 'monthly'
    
    def test_recurring_donation_str_representation(self):
        """Test the string representation of a recurring donation"""
        donor = DonorFactory(first_name='Jane', last_name='Smith')
        recurring = RecurringDonationFactory(
            donor=donor,
            amount=Decimal('50.00'),
            frequency='monthly'
        )
        
        str_repr = str(recurring)
        assert 'Jane Smith' in str_repr or 'Smith' in str_repr
        assert 'monthly' in str_repr.lower() or '50' in str_repr
    
    def test_recurring_donation_frequency_choices(self):
        """Test recurring donation frequency choices"""
        donor = DonorFactory()
        
        for frequency in ['weekly', 'monthly', 'quarterly', 'yearly']:
            recurring = RecurringDonationFactory(donor=donor, frequency=frequency)
            assert recurring.frequency == frequency
    
    def test_recurring_donation_status_choices(self):
        """Test recurring donation status choices"""
        donor = DonorFactory()
        
        for status in ['active', 'paused', 'cancelled', 'completed']:
            recurring = RecurringDonationFactory(donor=donor, status=status)
            assert recurring.status == status
    
    def test_recurring_donation_amount_must_be_positive(self):
        """Test that recurring donation amount must be positive"""
        donor = DonorFactory()
        
        with pytest.raises(Exception):
            RecurringDonationFactory(donor=donor, amount=Decimal('-25.00'))
    
    def test_recurring_donation_dates(self):
        """Test recurring donation date fields"""
        donor = DonorFactory()
        recurring = RecurringDonationFactory(
            donor=donor,
            start_date='2024-01-01',
            end_date='2024-12-31'
        )
        
        assert recurring.start_date is not None
        assert recurring.end_date is not None
    
    def test_recurring_donation_tracking_fields(self):
        """Test recurring donation tracking fields"""
        donor = DonorFactory()
        recurring = RecurringDonationFactory(
            donor=donor,
            total_donations=12,
            total_amount=Decimal('300.00')
        )
        
        assert recurring.total_donations == 12
        assert recurring.total_amount == Decimal('300.00')
    
    def test_recurring_donation_payment_method(self):
        """Test recurring donation payment method"""
        donor = DonorFactory()
        recurring = RecurringDonationFactory(
            donor=donor,
            payment_method='credit_card'
        )
        
        assert recurring.payment_method == 'credit_card'
    
    def test_recurring_donation_cascade_delete(self):
        """Test that recurring donations are deleted when donor is deleted"""
        donor = DonorFactory()
        recurring = RecurringDonationFactory(donor=donor)
        recurring_id = recurring.id
        
        donor.delete()
        
        with pytest.raises(RecurringDonation.DoesNotExist):
            RecurringDonation.objects.get(id=recurring_id)
    
    def test_recurring_donation_lifecycle_active_to_cancelled(self):
        """Test recurring donation lifecycle from active to cancelled"""
        donor = DonorFactory()
        recurring = RecurringDonationFactory(donor=donor, status='active')
        
        assert recurring.status == 'active'
        
        # Cancel the recurring donation
        recurring.status = 'cancelled'
        recurring.save()
        
        updated = RecurringDonation.objects.get(id=recurring.id)
        assert updated.status == 'cancelled'
    
    def test_recurring_donation_lifecycle_active_to_paused(self):
        """Test pausing and resuming a recurring donation"""
        donor = DonorFactory()
        recurring = RecurringDonationFactory(donor=donor, status='active')
        
        # Pause
        recurring.status = 'paused'
        recurring.save()
        assert RecurringDonation.objects.get(id=recurring.id).status == 'paused'
        
        # Resume
        recurring.status = 'active'
        recurring.save()
        assert RecurringDonation.objects.get(id=recurring.id).status == 'active'


@pytest.mark.django_db
class TestDonationsIntegration:
    """Integration tests for donation-related functionality"""
    
    def test_donor_with_multiple_donations(self):
        """Test a donor with multiple donations"""
        donor = DonorFactory()
        
        donation1 = DonationFactory(donor=donor, amount=Decimal('50.00'))
        donation2 = DonationFactory(donor=donor, amount=Decimal('75.00'))
        donation3 = DonationFactory(donor=donor, amount=Decimal('100.00'))
        
        assert donor.donations.count() == 3
        
        total = sum(d.amount for d in donor.donations.all())
        assert total == Decimal('225.00')
    
    def test_donor_with_recurring_and_one_time(self):
        """Test a donor with both recurring and one-time donations"""
        donor = DonorFactory()
        
        # One-time donation
        one_time = DonationFactory(
            donor=donor,
            amount=Decimal('100.00')
        )
        
        # Recurring donation setup
        recurring = RecurringDonationFactory(
            donor=donor,
            amount=Decimal('25.00'),
            frequency='monthly'
        )
        
        assert donor.donations.count() >= 1
        assert donor.recurring_donations.count() == 1
    
    def test_campaign_donation_tracking(self):
        """Test tracking donations by campaign"""
        donor1 = DonorFactory()
        donor2 = DonorFactory()
        
        # Donations to same campaign
        donation1 = DonationFactory(donor=donor1, campaign='Spring2024', amount=Decimal('100.00'))
        donation2 = DonationFactory(donor=donor2, campaign='Spring2024', amount=Decimal('150.00'))
        donation3 = DonationFactory(donor=donor1, campaign='Fall2024', amount=Decimal('75.00'))
        
        spring_donations = Donation.objects.filter(campaign='Spring2024')
        assert spring_donations.count() == 2
        
        spring_total = sum(d.amount for d in spring_donations)
        assert spring_total == Decimal('250.00')
