from django.contrib import admin
from .models import Event, EventRegistration, EventSponsor, EventTask


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'event_type', 'status', 'start_date', 'venue_city', 'actual_attendees', 'total_raised', 'fundraising_goal']
    list_filter = ['status', 'event_type', 'is_virtual', 'is_invite_only']
    search_fields = ['name', 'venue_name', 'venue_city', 'description']
    readonly_fields = ['actual_attendees', 'total_raised', 'total_expenses', 'created_at', 'updated_at']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Event Information', {
            'fields': ('name', 'description', 'event_type', 'status', 'campaign')
        }),
        ('Date & Time', {
            'fields': ('start_date', 'end_date', 'setup_date')
        }),
        ('Location', {
            'fields': ('is_virtual', 'venue_name', 'venue_address', 'venue_city', 'venue_state', 'venue_postal_code', 'venue_country', 'virtual_event_url')
        }),
        ('Capacity & Registration', {
            'fields': ('capacity', 'registration_deadline', 'requires_registration', 'is_invite_only')
        }),
        ('Financial Goals', {
            'fields': ('fundraising_goal', 'ticket_price', 'sponsor_goal', 'actual_attendees', 'total_raised', 'total_expenses')
        }),
        ('Notes & Custom Fields', {
            'fields': ('notes', 'custom_fields'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class EventRegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 0
    readonly_fields = ['registered_at', 'checked_in_at']
    fields = ['donor', 'status', 'number_of_guests', 'amount_paid', 'checked_in_at']


class EventSponsorInline(admin.TabularInline):
    model = EventSponsor
    extra = 0
    fields = ['sponsor_name', 'level', 'amount', 'status']


class EventTaskInline(admin.TabularInline):
    model = EventTask
    extra = 0
    fields = ['title', 'status', 'priority', 'assigned_to', 'due_date']


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['donor', 'event', 'status', 'number_of_guests', 'amount_paid', 'checked_in_at']
    list_filter = ['status', 'event__event_type']
    search_fields = ['donor__first_name', 'donor__last_name', 'donor__email', 'event__name']
    readonly_fields = ['registered_at', 'updated_at', 'checked_in_at', 'checked_in_by']
    date_hierarchy = 'registered_at'
    
    fieldsets = (
        ('Registration', {
            'fields': ('event', 'donor', 'status')
        }),
        ('Guests & Requirements', {
            'fields': ('number_of_guests', 'dietary_requirements', 'special_requests')
        }),
        ('Payment', {
            'fields': ('amount_paid', 'payment_method', 'payment_reference')
        }),
        ('Check-in', {
            'fields': ('checked_in_at', 'checked_in_by')
        }),
        ('Metadata', {
            'fields': ('created_by', 'registered_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EventSponsor)
class EventSponsorAdmin(admin.ModelAdmin):
    list_display = ['sponsor_name', 'event', 'level', 'amount', 'status']
    list_filter = ['level', 'status']
    search_fields = ['sponsor_name', 'event__name', 'sponsor_contact__first_name', 'sponsor_contact__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Sponsor Information', {
            'fields': ('event', 'sponsor_name', 'sponsor_contact', 'level', 'amount', 'status')
        }),
        ('Benefits', {
            'fields': ('benefits_description', 'logo_url', 'website_url')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EventTask)
class EventTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'event', 'status', 'priority', 'assigned_to', 'due_date', 'completed_at']
    list_filter = ['status', 'priority', 'event__event_type']
    search_fields = ['title', 'description', 'event__name']
    readonly_fields = ['completed_at', 'created_at', 'updated_at']
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('Task Information', {
            'fields': ('event', 'title', 'description', 'status', 'priority')
        }),
        ('Assignment & Due Date', {
            'fields': ('assigned_to', 'due_date')
        }),
        ('Completion', {
            'fields': ('completed_at', 'completed_by')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
