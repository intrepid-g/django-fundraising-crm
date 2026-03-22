from django.contrib import admin
from .models import Donor


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'donor_type', 'total_donations', 'donation_count', 'created_at']
    list_filter = ['donor_type', 'email_opt_in', 'country']
    search_fields = ['first_name', 'last_name', 'email', 'organization_name']
    readonly_fields = ['total_donations', 'donation_count', 'first_donation_date', 'last_donation_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'donor_type', 'organization_name')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Donation Statistics', {
            'fields': ('total_donations', 'donation_count', 'first_donation_date', 'last_donation_date'),
            'classes': ('collapse',)
        }),
        ('Tags & Segments', {
            'fields': ('tags', 'segments')
        }),
        ('Communication', {
            'fields': ('email_opt_in', 'email_preferences')
        }),
        ('Notes & Custom Fields', {
            'fields': ('notes', 'custom_fields')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
