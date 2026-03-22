from django.db import models
from django.contrib.auth.models import User
from donors.models import Donor


class Communication(models.Model):
    """Track all communications with donors (emails, calls, meetings, notes)."""
    
    EMAIL = 'email'
    PHONE = 'phone'
    MEETING = 'meeting'
    NOTE = 'note'
    LETTER = 'letter'
    SMS = 'sms'
    SOCIAL_MEDIA = 'social_media'
    VIDEO_CALL = 'video_call'
    
    COMMUNICATION_TYPES = [
        (EMAIL, 'Email'),
        (PHONE, 'Phone Call'),
        (MEETING, 'In-Person Meeting'),
        (NOTE, 'Note'),
        (LETTER, 'Letter/Mail'),
        (SMS, 'SMS/Text'),
        (SOCIAL_MEDIA, 'Social Media'),
        (VIDEO_CALL, 'Video Call'),
    ]
    
    INBOUND = 'inbound'
    OUTBOUND = 'outbound'
    
    DIRECTION_CHOICES = [
        (INBOUND, 'Inbound'),
        (OUTBOUND, 'Outbound'),
    ]
    
    PENDING = 'pending'
    SENT = 'sent'
    DELIVERED = 'delivered'
    READ = 'read'
    REPLIED = 'replied'
    FAILED = 'failed'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SENT, 'Sent'),
        (DELIVERED, 'Delivered'),
        (READ, 'Read'),
        (REPLIED, 'Replied'),
        (FAILED, 'Failed'),
    ]
    
    # Core relationship
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='communications')
    
    # Communication details
    communication_type = models.CharField(max_length=20, choices=COMMUNICATION_TYPES)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES, default=OUTBOUND)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    
    # Content
    subject = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    summary = models.TextField(blank=True, help_text="Brief summary of the communication")
    
    # Contact information
    from_address = models.CharField(max_length=255, blank=True)
    to_address = models.CharField(max_length=255, blank=True)
    
    # Timing
    communication_date = models.DateTimeField()
    scheduled_date = models.DateTimeField(null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    delivered_date = models.DateTimeField(null=True, blank=True)
    read_date = models.DateTimeField(null=True, blank=True)
    
    # Follow-up
    requires_followup = models.BooleanField(default=False)
    followup_date = models.DateTimeField(null=True, blank=True)
    followup_completed = models.BooleanField(default=False)
    
    # Sentiment/Outcome
    sentiment = models.CharField(max_length=20, blank=True, help_text="positive, neutral, negative")
    outcome = models.CharField(max_length=50, blank=True, help_text="pledge_made, donation_received, meeting_scheduled, etc.")
    
    # Related records
    related_donation = models.ForeignKey(
        'donations.Donation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='communications'
    )
    related_event = models.ForeignKey(
        'events.Event',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='communications'
    )
    
    # Attachments (JSON for flexibility)
    attachments = models.JSONField(default=list, blank=True)
    
    # External IDs (for email tracking, etc.)
    external_id = models.CharField(max_length=255, blank=True)
    thread_id = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-communication_date']
        indexes = [
            models.Index(fields=['donor', 'communication_date']),
            models.Index(fields=['communication_type', 'communication_date']),
            models.Index(fields=['status', 'requires_followup']),
            models.Index(fields=['thread_id']),
        ]
    
    def __str__(self):
        return f"{self.donor} - {self.get_communication_type_display()} ({self.communication_date.strftime('%Y-%m-%d')})"


class CommunicationTemplate(models.Model):
    """Reusable templates for common communications."""
    
    EMAIL = 'email'
    SMS = 'sms'
    LETTER = 'letter'
    
    TEMPLATE_TYPES = [
        (EMAIL, 'Email'),
        (SMS, 'SMS'),
        (LETTER, 'Letter'),
    ]
    
    # Template details
    name = models.CharField(max_length=255)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    subject_template = models.CharField(max_length=255, blank=True)
    body_template = models.TextField()
    
    # Usage
    category = models.CharField(max_length=50, blank=True, help_text="thank_you, welcome, reminder, etc.")
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    # Variables available in template
    available_variables = models.JSONField(default=list, blank=True, help_text="List of available template variables")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['template_type', 'category']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def render(self, context):
        """Render template with given context."""
        from django.template import Template, Context
        
        subject = Template(self.subject_template).render(Context(context)) if self.subject_template else ""
        body = Template(self.body_template).render(Context(context))
        
        return {"subject": subject, "body": body}


class CommunicationSchedule(models.Model):
    """Scheduled communications (automated or manual)."""
    
    PENDING = 'pending'
    PROCESSING = 'processing'
    SENT = 'sent'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (SENT, 'Sent'),
        (FAILED, 'Failed'),
        (CANCELLED, 'Cancelled'),
    ]
    
    # Core relationship
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='scheduled_communications')
    template = models.ForeignKey(
        CommunicationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scheduled_uses'
    )
    
    # Schedule details
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    
    # Content (if not using template)
    subject = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    
    # Template context
    template_context = models.JSONField(default=dict, blank=True)
    
    # Automation
    is_automated = models.BooleanField(default=False)
    automation_trigger = models.CharField(max_length=50, blank=True, help_text="new_donor, first_donation, lapsed_donor, etc.")
    
    # Execution tracking
    sent_date = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['scheduled_date']
        indexes = [
            models.Index(fields=['donor', 'scheduled_date']),
            models.Index(fields=['status', 'scheduled_date']),
            models.Index(fields=['is_automated', 'status']),
        ]
    
    def __str__(self):
        return f"{self.donor} - {self.scheduled_date.strftime('%Y-%m-%d %H:%M')}"


class CommunicationPreference(models.Model):
    """Donor communication preferences."""
    
    donor = models.OneToOneField(Donor, on_delete=models.CASCADE, related_name='communication_preference')
    
    # Channel preferences
    email_opt_in = models.BooleanField(default=True)
    phone_opt_in = models.BooleanField(default=True)
    sms_opt_in = models.BooleanField(default=False)
    mail_opt_in = models.BooleanField(default=True)
    
    # Frequency
    preferred_frequency = models.CharField(
        max_length=20,
        default='monthly',
        choices=[
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('annually', 'Annually'),
            ('as_needed', 'As Needed'),
        ]
    )
    
    # Content preferences
    preferred_topics = models.JSONField(default=list, blank=True)
    exclude_topics = models.JSONField(default=list, blank=True)
    
    # Timing
    preferred_contact_time = models.CharField(max_length=50, blank=True, help_text="morning, afternoon, evening")
    timezone = models.CharField(max_length=50, default='America/New_York')
    
    # Do not contact
    do_not_contact = models.BooleanField(default=False)
    do_not_contact_reason = models.TextField(blank=True)
    do_not_contact_until = models.DateField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.donor} Preferences"
    
    def can_contact(self, channel='email'):
        """Check if donor can be contacted via given channel."""
        if self.do_not_contact:
            if self.do_not_contact_until and self.do_not_contact_until > timezone.now().date():
                return False
        
        channel_map = {
            'email': self.email_opt_in,
            'phone': self.phone_opt_in,
            'sms': self.sms_opt_in,
            'mail': self.mail_opt_in,
        }
        
        return channel_map.get(channel, False)


class CallLog(models.Model):
    """Detailed phone call logs."""
    
    communication = models.OneToOneField(
        Communication,
        on_delete=models.CASCADE,
        related_name='call_details'
    )
    
    # Call details
    phone_number = models.CharField(max_length=20)
    duration_seconds = models.PositiveIntegerField(default=0)
    was_answered = models.BooleanField(default=False)
    went_to_voicemail = models.BooleanField(default=False)
    
    # Call quality
    call_quality = models.CharField(max_length=20, blank=True, help_text="excellent, good, fair, poor")
    recording_url = models.URLField(blank=True)
    
    # Outcome
    call_outcome = models.CharField(max_length=50, blank=True, help_text="spoke_to_donor, left_message, no_answer, busy, wrong_number")
    follow_up_required = models.BooleanField(default=False)
    follow_up_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Call to {self.phone_number} ({self.duration_seconds}s)"
    
    @property
    def duration_formatted(self):
        """Return formatted duration (MM:SS)."""
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"
