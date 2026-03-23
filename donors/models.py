from django.db import models
from django.contrib.auth.models import User


class Donor(models.Model):
    """Donor model with tags and segments for CRM."""
    
    INDIVIDUAL = 'individual'
    ORGANIZATION = 'organization'
    FOUNDATION = 'foundation'
    
    DONOR_TYPES = [
        (INDIVIDUAL, 'Individual'),
        (ORGANIZATION, 'Organization'),
        (FOUNDATION, 'Foundation'),
    ]
    
    # Basic information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Address
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='US')
    
    # Donor metadata
    donor_type = models.CharField(max_length=20, choices=DONOR_TYPES, default=INDIVIDUAL)
    organization_name = models.CharField(max_length=255, blank=True)
    
    # Tags and segments (JSON for flexibility)
    tags = models.JSONField(default=list, blank=True)
    segments = models.JSONField(default=list, blank=True)
    
    # Tracking
    first_donation_date = models.DateField(null=True, blank=True)
    last_donation_date = models.DateField(null=True, blank=True)
    total_donations = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    donation_count = models.PositiveIntegerField(default=0)
    
    # Communication preferences
    email_opt_in = models.BooleanField(default=True)
    email_preferences = models.JSONField(default=dict, blank=True)
    
    # Notes and custom fields
    notes = models.TextField(blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['donor_type']),
        ]
    
    @property
    def full_name(self):
        """Return donor's full name."""
        if self.organization_name:
            return self.organization_name
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def formatted_address(self):
        """Return formatted address string."""
        parts = []
        if self.address_line1:
            parts.append(self.address_line1)
        if self.address_line2:
            parts.append(self.address_line2)
        city_state = []
        if self.city:
            city_state.append(self.city)
        if self.state:
            city_state.append(self.state)
        if city_state:
            parts.append(", ".join(city_state))
        if self.postal_code:
            parts.append(self.postal_code)
        if self.country and self.country != 'US':
            parts.append(self.country)
        return "\n".join(parts)
    
    def __str__(self):
        if self.organization_name:
            return f"{self.organization_name} ({self.email})"
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def update_donation_stats(self):
        """Update donation statistics."""
        from donations.models import Donation
        
        donations = Donation.objects.filter(donor=self, status='completed')
        self.donation_count = donations.count()
        self.total_donations = donations.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        if donations.exists():
            self.first_donation_date = donations.order_by('donation_date').first().donation_date
            self.last_donation_date = donations.order_by('-donation_date').first().donation_date
        
        self.save(update_fields=[
            'donation_count', 'total_donations',
            'first_donation_date', 'last_donation_date'
        ])


class DonorNote(models.Model):
    """Notes attached to donors."""
    
    NOTE_TYPES = [
        ('general', 'General'),
        ('interaction', 'Interaction'),
        ('preference', 'Preference'),
        ('alert', 'Alert'),
    ]
    
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donor_notes')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default='general')
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note on {self.donor} by {self.author}"


class DonorInteraction(models.Model):
    """Track interactions with donors (calls, meetings, etc.)."""
    
    INTERACTION_TYPES = [
        ('phone_call', 'Phone Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('event', 'Event'),
        ('mail', 'Mail'),
        ('social_media', 'Social Media'),
        ('other', 'Other'),
    ]
    
    DIRECTIONS = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]
    
    OUTCOMES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
        ('follow_up_required', 'Follow-up Required'),
    ]
    
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='interactions')
    staff_member = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    direction = models.CharField(max_length=10, choices=DIRECTIONS, default='outbound')
    subject = models.CharField(max_length=255, blank=True)
    summary = models.TextField(blank=True)
    outcome = models.CharField(max_length=20, choices=OUTCOMES, blank=True)
    
    # Follow-up tracking
    requires_followup = models.BooleanField(default=False)
    followup_date = models.DateField(null=True, blank=True)
    followup_completed = models.BooleanField(default=False)
    
    # Timestamps
    interaction_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-interaction_date']
    
    def __str__(self):
        return f"{self.get_interaction_type_display()} with {self.donor}"
