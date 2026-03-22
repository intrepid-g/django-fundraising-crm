from django.db import models
from django.contrib.auth.models import User
from donors.models import Donor


class Campaign(models.Model):
    """Fundraising campaign."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name


class Donation(models.Model):
    """Donation model supporting one-time, recurring, and pledges."""
    
    ONE_TIME = 'one_time'
    RECURRING = 'recurring'
    PLEDGE = 'pledge'
    
    DONATION_TYPES = [
        (ONE_TIME, 'One-Time'),
        (RECURRING, 'Recurring'),
        (PLEDGE, 'Pledge'),
    ]
    
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
        (REFUNDED, 'Refunded'),
        (CANCELLED, 'Cancelled'),
    ]
    
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    ANNUALLY = 'annually'
    
    FREQUENCY_CHOICES = [
        (MONTHLY, 'Monthly'),
        (QUARTERLY, 'Quarterly'),
        (ANNUALLY, 'Annually'),
    ]
    
    # Core fields
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donations')
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations')
    
    # Donation details
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    donation_type = models.CharField(max_length=20, choices=DONATION_TYPES, default=ONE_TIME)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, blank=True)
    
    # Status and dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    donation_date = models.DateField(db_index=True)
    received_date = models.DateField(null=True, blank=True)
    
    # Payment information
    payment_method = models.CharField(max_length=50, blank=True)  # credit_card, bank_transfer, check, etc.
    payment_reference = models.CharField(max_length=255, blank=True)  # Transaction ID, check number, etc.
    
    # Recurring donation tracking
    parent_donation = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_donations')
    recurring_end_date = models.DateField(null=True, blank=True)
    
    # Additional information
    notes = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    is_tax_deductible = models.BooleanField(default=True)
    
    # Tribute/honorary fields
    is_tribute = models.BooleanField(default=False)
    tribute_type = models.CharField(max_length=50, blank=True)  # in_memory, in_honor
    tribute_honoree = models.CharField(max_length=255, blank=True)
    tribute_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-donation_date', '-created_at']
        indexes = [
            models.Index(fields=['donor', 'donation_date']),
            models.Index(fields=['campaign', 'donation_date']),
            models.Index(fields=['status', 'donation_date']),
        ]
    
    def __str__(self):
        return f"{self.donor} - ${self.amount} ({self.get_donation_type_display()})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update donor stats after saving
        if self.status == self.COMPLETED:
            self.donor.update_donation_stats()
