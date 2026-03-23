from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from donors.models import Donor
from donations.models import Campaign


class Event(models.Model):
    """Fundraising event (galas, dinners, auctions, etc.)."""
    
    GALA = 'gala'
    DINNER = 'dinner'
    AUCTION = 'auction'
    GOLF_TOURNAMENT = 'golf_tournament'
    WALKATHON = 'walkathon'
    CONCERT = 'concert'
    MEETING = 'meeting'
    OTHER = 'other'
    
    EVENT_TYPES = [
        (GALA, 'Gala'),
        (DINNER, 'Dinner'),
        (AUCTION, 'Auction'),
        (GOLF_TOURNAMENT, 'Golf Tournament'),
        (WALKATHON, 'Walkathon'),
        (CONCERT, 'Concert'),
        (MEETING, 'Meeting'),
        (OTHER, 'Other'),
    ]
    
    DRAFT = 'draft'
    PLANNING = 'planning'
    CONFIRMED = 'confirmed'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PLANNING, 'Planning'),
        (CONFIRMED, 'Confirmed'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]
    
    # Basic information
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default=OTHER)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    
    # Date and time
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    setup_date = models.DateTimeField(null=True, blank=True)
    
    # Location
    venue_name = models.CharField(max_length=255, blank=True)
    venue_address = models.CharField(max_length=255, blank=True)
    venue_city = models.CharField(max_length=100, blank=True)
    venue_state = models.CharField(max_length=100, blank=True)
    venue_postal_code = models.CharField(max_length=20, blank=True)
    venue_country = models.CharField(max_length=100, default='US')
    virtual_event_url = models.URLField(blank=True)
    is_virtual = models.BooleanField(default=False)
    
    # Capacity and registration
    capacity = models.PositiveIntegerField(null=True, blank=True)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    requires_registration = models.BooleanField(default=True)
    is_invite_only = models.BooleanField(default=False)
    
    # Financial goals
    fundraising_goal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sponsor_goal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Campaign association
    campaign = models.ForeignKey(
        Campaign, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='events'
    )
    
    # Tracking
    actual_attendees = models.PositiveIntegerField(default=0)
    total_raised = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Notes and custom fields
    notes = models.TextField(blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['start_date']),
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['event_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.start_date.strftime('%Y-%m-%d')})"

    def clean(self):
        """Validate event data."""
        super().clean()

        # Validate end date is after start date
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError("End date must be after start date.")

        # Validate capacity is not zero (if set)
        if self.capacity is not None and self.capacity == 0:
            raise ValidationError("Capacity cannot be zero.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def update_financials(self):
        """Update event financial statistics."""
        from django.db.models import Sum
        
        registrations = self.registrations.filter(status='confirmed')
        self.actual_attendees = registrations.count()
        self.total_raised = registrations.aggregate(
            total=Sum('amount_paid')
        )['total'] or 0
        
        self.save(update_fields=['actual_attendees', 'total_raised'])


class EventRegistration(models.Model):
    """Event registration/RSVP for donors."""

    PENDING = 'pending'
    REGISTERED = 'registered'
    CONFIRMED = 'confirmed'
    ATTENDED = 'attended'
    CANCELLED = 'cancelled'
    NO_SHOW = 'no_show'
    WAITLISTED = 'waitlisted'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (REGISTERED, 'Registered'),
        (CONFIRMED, 'Confirmed'),
        (ATTENDED, 'Attended'),
        (CANCELLED, 'Cancelled'),
        (NO_SHOW, 'No Show'),
        (WAITLISTED, 'Waitlisted'),
    ]
    
    # Core relationship
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='event_registrations')
    
    # Registration details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=REGISTERED)
    number_of_guests = models.PositiveIntegerField(default=1)
    dietary_requirements = models.TextField(blank=True)
    special_requests = models.TextField(blank=True)
    
    # Financial
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=255, blank=True)
    
    # Check-in
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_in_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='event_checkins'
    )

    # Cancellation
    cancellation_date = models.DateField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)

    # Waitlist
    waitlist_position = models.PositiveIntegerField(null=True, blank=True)

    # Timestamps
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_registrations'
    )
    
    class Meta:
        ordering = ['-registered_at']
        unique_together = ['event', 'donor']
        indexes = [
            models.Index(fields=['event', 'status']),
            models.Index(fields=['donor', 'status']),
        ]
    
    def __str__(self):
        return f"{self.donor} - {self.event}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update event statistics
        self.event.update_financials()


class EventSponsor(models.Model):
    """Event sponsor."""

    PLATINUM = 'platinum'
    GOLD = 'gold'
    SILVER = 'silver'
    BRONZE = 'bronze'
    IN_KIND = 'in_kind'

    SPONSOR_LEVELS = [
        (PLATINUM, 'Platinum'),
        (GOLD, 'Gold'),
        (SILVER, 'Silver'),
        (BRONZE, 'Bronze'),
        (IN_KIND, 'In-Kind'),
    ]

    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    PAID = 'paid'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (PAID, 'Paid'),
    ]

    # Core relationship
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='sponsors')
    sponsor_name = models.CharField(max_length=255)
    sponsor_contact = models.ForeignKey(
        Donor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='event_sponsorships'
    )

    # Sponsorship details
    level = models.CharField(max_length=20, choices=SPONSOR_LEVELS, default=BRONZE)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_pledged = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    # Benefits
    benefits_description = models.TextField(blank=True)
    logo_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)

    # Legacy/alias fields for test compatibility
    @property
    def donor(self):
        return self.sponsor_contact

    @donor.setter
    def donor(self, value):
        self.sponsor_contact = value

    @property
    def sponsor_level(self):
        return self.level

    @sponsor_level.setter
    def sponsor_level(self, value):
        self.level = value

    @property
    def benefits_provided(self):
        """Parse benefits_description as a list."""
        if not self.benefits_description:
            return []
        return [b.strip() for b in self.benefits_description.split(',') if b.strip()]

    @benefits_provided.setter
    def benefits_provided(self, value):
        """Store list as comma-separated string."""
        if isinstance(value, list):
            self.benefits_description = ', '.join(str(v) for v in value)
        else:
            self.benefits_description = str(value) if value else ''
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-amount', 'level']
        indexes = [
            models.Index(fields=['event', 'status']),
            models.Index(fields=['level']),
        ]
    
    def __str__(self):
        return f"{self.sponsor_name} - {self.event} ({self.get_level_display()})"


class EventTask(models.Model):
    """Task/checklist item for event planning."""

    PENDING = 'pending'
    TODO = 'todo'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (TODO, 'To Do'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]

    URGENT = 'urgent'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'

    PRIORITY_CHOICES = [
        (URGENT, 'Urgent'),
        (HIGH, 'High'),
        (MEDIUM, 'Medium'),
        (LOW, 'Low'),
    ]
    
    # Core relationship
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tasks')
    
    # Task details
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=TODO)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=MEDIUM)
    
    # Assignment
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='event_tasks'
    )
    due_date = models.DateTimeField(null=True, blank=True)
    
    # Completion
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='completed_event_tasks'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['due_date', '-priority', 'title']
        indexes = [
            models.Index(fields=['event', 'status']),
            models.Index(fields=['assigned_to', 'status']),
        ]
    
    def __str__(self):
        return f"{self.event} - {self.title}"
