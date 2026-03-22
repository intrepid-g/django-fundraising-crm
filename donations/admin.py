from django.contrib import admin
from .models import Donation, Campaign


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'goal_amount', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['donor', 'amount', 'donation_type', 'status', 'donation_date', 'campaign']
    list_filter = ['donation_type', 'status', 'is_anonymous', 'is_tax_deductible', 'campaign']
    search_fields = ['donor__first_name', 'donor__last_name', 'donor__email', 'payment_reference']
    date_hierarchy = 'donation_date'
    raw_id_fields = ['donor', 'parent_donation']
    
    fieldsets = (
        ('Donor & Campaign', {
            'fields': ('donor', 'campaign')
        }),
        ('Donation Details', {
            'fields': ('amount', 'donation_type', 'frequency', 'status', 'donation_date', 'received_date')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_reference')
        }),
        ('Recurring Donation', {
            'fields': ('parent_donation', 'recurring_end_date'),
            'classes': ('collapse',)
        }),
        ('Tribute Information', {
            'fields': ('is_tribute', 'tribute_type', 'tribute_honoree', 'tribute_message'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'is_anonymous', 'is_tax_deductible')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
