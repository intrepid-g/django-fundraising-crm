"""
Donors app model tests
Comprehensive unit tests for Donor model
"""
import pytest
from django.core.exceptions import ValidationError
from donors.models import Donor
from factories import DonorFactory


@pytest.mark.django_db
class TestDonorModel:
    """Test cases for the Donor model"""
    
    def test_create_donor_with_valid_data(self):
        """Test creating a donor with all valid fields"""
        donor = DonorFactory()
        assert donor.id is not None
        assert donor.first_name is not None
        assert donor.last_name is not None
        assert donor.email is not None
    
    def test_donor_str_representation(self):
        """Test the string representation of a donor"""
        donor = DonorFactory(first_name='John', last_name='Doe')
        assert str(donor) == 'John Doe'
    
    def test_donor_full_name_property(self):
        """Test the full_name property"""
        donor = DonorFactory(first_name='Jane', last_name='Smith')
        assert donor.full_name == 'Jane Smith'
    
    def test_donor_email_unique_constraint(self):
        """Test that donor emails must be unique"""
        donor1 = DonorFactory(email='unique@example.com')
        with pytest.raises(Exception):  # IntegrityError
            DonorFactory(email='unique@example.com')
    
    def test_donor_donor_type_choices(self):
        """Test donor type choices are valid"""
        for donor_type in ['individual', 'corporate', 'foundation']:
            donor = DonorFactory(donor_type=donor_type)
            assert donor.donor_type == donor_type
    
    def test_donor_timestamps_auto_set(self):
        """Test that created_at and updated_at are set automatically"""
        donor = DonorFactory()
        assert donor.created_at is not None
        assert donor.updated_at is not None
    
    def test_donor_update_fields(self):
        """Test updating donor fields"""
        donor = DonorFactory(first_name='Old', last_name='Name')
        donor.first_name = 'New'
        donor.last_name = 'Name2'
        donor.save()
        
        updated_donor = Donor.objects.get(id=donor.id)
        assert updated_donor.first_name == 'New'
        assert updated_donor.last_name == 'Name2'
    
    def test_donor_delete(self):
        """Test deleting a donor"""
        donor = DonorFactory()
        donor_id = donor.id
        donor.delete()
        
        with pytest.raises(Donor.DoesNotExist):
            Donor.objects.get(id=donor_id)
    
    def test_donor_optional_fields(self):
        """Test creating donor with minimal required fields"""
        donor = Donor.objects.create(
            first_name='Minimal',
            last_name='Donor',
            email='minimal@example.com'
        )
        assert donor.id is not None
    
    def test_donor_phone_field(self):
        """Test donor phone field"""
        donor = DonorFactory(phone='555-123-4567')
        assert donor.phone == '555-123-4567'
    
    def test_donor_total_donations_calculation(self):
        """Test total_donations property"""
        donor = DonorFactory()
        # Create some donations
        from factories import DonationFactory
        from decimal import Decimal
        DonationFactory(donor=donor, amount=Decimal('100.00'), status='completed')
        DonationFactory(donor=donor, amount=Decimal('200.00'), status='completed')
        
        assert donor.total_donations == Decimal('300.00')
    
    def test_donor_lifetime_value_calculation(self):
        """Test lifetime_value property"""
        donor = DonorFactory()
        from factories import DonationFactory
        from decimal import Decimal
        DonationFactory(donor=donor, amount=Decimal('500.00'), status='completed')
        
        assert donor.lifetime_value == Decimal('500.00')
    
    def test_donor_last_donation_date(self):
        """Test last_donation_date property"""
        donor = DonorFactory()
        from factories import DonationFactory
        from decimal import Decimal
        donation = DonationFactory(donor=donor, amount=Decimal('100.00'))
        
        assert donor.last_donation_date is not None
