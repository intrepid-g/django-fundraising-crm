from django.db import models
from django.contrib.auth.models import User
from donors.models import Donor
from donations.models import Donation, Campaign


class Report(models.Model):
    """Saved reports with configuration."""
    
    # Schedule frequency constants
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    
    DONOR_ANALYTICS = 'donor_analytics'
    DONATION_SUMMARY = 'donation_summary'
    CAMPAIGN_PERFORMANCE = 'campaign_performance'
    LTV_ANALYSIS = 'ltv_analysis'
    RETENTION_ANALYSIS = 'retention_analysis'
    EVENT_ANALYTICS = 'event_analytics'
    COMMUNICATION_ANALYTICS = 'communication_analytics'
    CUSTOM = 'custom'
    
    REPORT_TYPES = [
        (DONOR_ANALYTICS, 'Donor Analytics'),
        (DONATION_SUMMARY, 'Donation Summary'),
        (CAMPAIGN_PERFORMANCE, 'Campaign Performance'),
        (LTV_ANALYSIS, 'Lifetime Value Analysis'),
        (RETENTION_ANALYSIS, 'Retention Analysis'),
        (EVENT_ANALYTICS, 'Event Analytics'),
        (COMMUNICATION_ANALYTICS, 'Communication Analytics'),
        (CUSTOM, 'Custom Report'),
    ]
    
    # Report details
    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    
    # Configuration
    filters = models.JSONField(default=dict, blank=True, help_text="Report filters configuration")
    group_by = models.JSONField(default=list, blank=True, help_text="Grouping configuration")
    metrics = models.JSONField(default=list, blank=True, help_text="Metrics to include")
    sort_order = models.JSONField(default=list, blank=True, help_text="Sort configuration")
    
    # Date range
    date_range_start = models.DateField(null=True, blank=True)
    date_range_end = models.DateField(null=True, blank=True)
    date_range_preset = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('this_week', 'This Week'),
            ('last_week', 'Last Week'),
            ('this_month', 'This Month'),
            ('last_month', 'Last Month'),
            ('this_quarter', 'This Quarter'),
            ('last_quarter', 'Last Quarter'),
            ('this_year', 'This Year'),
            ('last_year', 'Last Year'),
            ('last_30_days', 'Last 30 Days'),
            ('last_90_days', 'Last 90 Days'),
            ('last_12_months', 'Last 12 Months'),
            ('all_time', 'All Time'),
            ('custom', 'Custom Range'),
        ]
    )
    
    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
        ]
    )
    schedule_day_of_week = models.PositiveSmallIntegerField(null=True, blank=True, help_text="0=Monday, 6=Sunday")
    schedule_day_of_month = models.PositiveSmallIntegerField(null=True, blank=True)
    
    # Recipients for scheduled reports
    schedule_recipients = models.JSONField(default=list, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_favorite = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-is_favorite', '-updated_at']
        indexes = [
            models.Index(fields=['report_type', 'is_active']),
            models.Index(fields=['created_by', 'is_favorite']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"


class Dashboard(models.Model):
    """Custom dashboards with widgets."""
    
    # Dashboard details
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Layout
    layout_config = models.JSONField(default=dict, blank=True, help_text="Dashboard layout configuration")
    
    # Widgets (JSON array of widget configurations)
    widgets = models.JSONField(default=list, blank=True, help_text="Widget configurations")
    
    # Status
    is_default = models.BooleanField(default=False, help_text="Default dashboard for user")
    is_shared = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-is_default', '-updated_at']
    
    def __str__(self):
        return f"{self.name} {'(Default)' if self.is_default else ''}"


class ReportExecution(models.Model):
    """Record of report executions."""
    
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (RUNNING, 'Running'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    ]
    
    # Execution details
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='executions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    
    # Parameters used
    parameters = models.JSONField(default=dict, blank=True)
    
    # Results
    result_data = models.JSONField(default=dict, blank=True, help_text="Report results")
    result_summary = models.JSONField(default=dict, blank=True, help_text="Summary statistics")
    row_count = models.PositiveIntegerField(default=0)
    
    # Output
    output_format = models.CharField(
        max_length=10,
        default='json',
        choices=[
            ('json', 'JSON'),
            ('csv', 'CSV'),
            ('xlsx', 'Excel'),
            ('pdf', 'PDF'),
        ]
    )
    output_file = models.FileField(upload_to='reports/', null=True, blank=True)
    
    # Performance
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    execution_time_seconds = models.PositiveIntegerField(default=0)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    executed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.report.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Calculate execution time
        if self.started_at and self.completed_at:
            self.execution_time_seconds = int((self.completed_at - self.started_at).total_seconds())
        super().save(*args, **kwargs)


class MetricDefinition(models.Model):
    """Predefined metrics for reports and dashboards."""
    
    DONOR = 'donor'
    DONATION = 'donation'
    CAMPAIGN = 'campaign'
    EVENT = 'event'
    COMMUNICATION = 'communication'
    
    ENTITY_TYPES = [
        (DONOR, 'Donor'),
        (DONATION, 'Donation'),
        (CAMPAIGN, 'Campaign'),
        (EVENT, 'Event'),
        (COMMUNICATION, 'Communication'),
    ]
    
    # Metric details
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    # Configuration
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    calculation_type = models.CharField(
        max_length=20,
        choices=[
            ('count', 'Count'),
            ('sum', 'Sum'),
            ('avg', 'Average'),
            ('min', 'Minimum'),
            ('max', 'Maximum'),
            ('distinct_count', 'Distinct Count'),
            ('custom', 'Custom'),
        ]
    )
    field_name = models.CharField(max_length=100, blank=True, help_text="Field to aggregate")
    
    # Formula for custom calculations
    custom_formula = models.TextField(blank=True, help_text="Custom calculation formula")
    
    # Formatting
    format_string = models.CharField(max_length=50, default='{value}', help_text="Format string for display")
    unit = models.CharField(max_length=20, blank=True, help_text="$, %, etc.")
    
    # Status
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False, help_text="System metric, cannot be deleted")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['entity_type', 'name']
        indexes = [
            models.Index(fields=['entity_type', 'is_active']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_entity_type_display()})", 