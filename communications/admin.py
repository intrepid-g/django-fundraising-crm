from django.contrib import admin
from .models import (
    Communication, CommunicationTemplate, CommunicationSchedule,
    CommunicationPreference, CallLog
)


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ['donor', 'communication_type', 'direction', 'status', 'subject', 'communication_date', 'requires_followup']
    list_filter = ['communication_type', 'direction', 'status', 'requires_followup', 'sentiment']
    search_fields = ['donor__first_name', 'donor__last_name', 'donor__email', 'subject', 'content', 'summary']
    readonly_fields = ['created_at', 'updated_at', 'sent_date', 'delivered_date', 'read_date']
    date_hierarchy = 'communication_date'
    
    fieldsets = (
        ('Communication Details', {
            'fields': ('donor', 'communication_type', 'direction', 'status')
        }),
        ('Content', {
            'fields': ('subject', 'content', 'summary')
        }),
        ('Addresses', {
            'fields': ('from_address', 'to_address')
        }),
        ('Timing', {
            'fields': ('communication_date', 'scheduled_date', 'sent_date', 'delivered_date', 'read_date')
        }),
        ('Follow-up', {
            'fields': ('requires_followup', 'followup_date', 'followup_completed')
        }),
        ('Outcome', {
            'fields': ('sentiment', 'outcome')
        }),
        ('Related Records', {
            'fields': ('related_donation', 'related_event')
        }),
        ('Tracking', {
            'fields': ('external_id', 'thread_id', 'attachments')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CommunicationTemplate)
class CommunicationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'category', 'is_active', 'usage_count', 'created_at']
    list_filter = ['template_type', 'category', 'is_active']
    search_fields = ['name', 'subject_template', 'body_template']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'template_type', 'category', 'is_active')
        }),
        ('Content', {
            'fields': ('subject_template', 'body_template', 'available_variables')
        }),
        ('Usage', {
            'fields': ('usage_count',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CommunicationSchedule)
class CommunicationScheduleAdmin(admin.ModelAdmin):
    list_display = ['donor', 'scheduled_date', 'status', 'is_automated', 'automation_trigger', 'sent_date']
    list_filter = ['status', 'is_automated', 'automation_trigger']
    search_fields = ['donor__first_name', 'donor__last_name', 'donor__email', 'subject', 'content']
    readonly_fields = ['created_at', 'updated_at', 'sent_date']
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('Schedule', {
            'fields': ('donor', 'template', 'scheduled_date', 'status')
        }),
        ('Content', {
            'fields': ('subject', 'content', 'template_context')
        }),
        ('Automation', {
            'fields': ('is_automated', 'automation_trigger')
        }),
        ('Execution', {
            'fields': ('sent_date', 'error_message')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CommunicationPreference)
class CommunicationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['donor', 'email_opt_in', 'phone_opt_in', 'sms_opt_in', 'mail_opt_in', 'preferred_frequency', 'do_not_contact']
    list_filter = ['email_opt_in', 'phone_opt_in', 'sms_opt_in', 'mail_opt_in', 'preferred_frequency', 'do_not_contact']
    search_fields = ['donor__first_name', 'donor__last_name', 'donor__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Channel Preferences', {
            'fields': ('donor', 'email_opt_in', 'phone_opt_in', 'sms_opt_in', 'mail_opt_in')
        }),
        ('Frequency & Topics', {
            'fields': ('preferred_frequency', 'preferred_topics', 'exclude_topics')
        }),
        ('Timing', {
            'fields': ('preferred_contact_time', 'timezone')
        }),
        ('Do Not Contact', {
            'fields': ('do_not_contact', 'do_not_contact_reason', 'do_not_contact_until')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CallLog)
class CallLogAdmin(admin.ModelAdmin):
    list_display = ['communication', 'phone_number', 'duration_seconds', 'was_answered', 'went_to_voicemail', 'call_outcome', 'follow_up_required']
    list_filter = ['was_answered', 'went_to_voicemail', 'call_outcome', 'follow_up_required', 'call_quality']
    search_fields = ['communication__donor__first_name', 'communication__donor__last_name', 'phone_number']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Call Details', {
            'fields': ('communication', 'phone_number', 'duration_seconds', 'was_answered', 'went_to_voicemail')
        }),
        ('Quality', {
            'fields': ('call_quality', 'recording_url')
        }),
        ('Outcome', {
            'fields': ('call_outcome', 'follow_up_required', 'follow_up_notes')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
