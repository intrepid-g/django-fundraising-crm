from django.contrib import admin
from .models import Report, Dashboard, ReportExecution, MetricDefinition


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'is_scheduled', 'is_favorite', 'is_active', 'last_run_at', 'created_at']
    list_filter = ['report_type', 'is_scheduled', 'is_favorite', 'is_active', 'date_range_preset']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'last_run_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Report Information', {
            'fields': ('name', 'report_type', 'description', 'is_active', 'is_favorite')
        }),
        ('Configuration', {
            'fields': ('filters', 'group_by', 'metrics', 'sort_order')
        }),
        ('Date Range', {
            'fields': ('date_range_preset', 'date_range_start', 'date_range_end')
        }),
        ('Scheduling', {
            'fields': ('is_scheduled', 'schedule_frequency', 'schedule_day_of_week', 'schedule_day_of_month', 'schedule_recipients')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'last_run_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'is_shared', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_default', 'is_shared', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Dashboard Information', {
            'fields': ('name', 'description', 'is_active', 'is_default', 'is_shared')
        }),
        ('Layout & Widgets', {
            'fields': ('layout_config', 'widgets')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ReportExecution)
class ReportExecutionAdmin(admin.ModelAdmin):
    list_display = ['report', 'status', 'row_count', 'output_format', 'execution_time_seconds', 'created_at']
    list_filter = ['status', 'output_format']
    search_fields = ['report__name', 'error_message']
    readonly_fields = ['created_at', 'started_at', 'completed_at', 'execution_time_seconds']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Execution', {
            'fields': ('report', 'status', 'parameters')
        }),
        ('Results', {
            'fields': ('result_summary', 'row_count', 'output_format', 'output_file')
        }),
        ('Performance', {
            'fields': ('started_at', 'completed_at', 'execution_time_seconds')
        }),
        ('Error', {
            'fields': ('error_message',)
        }),
        ('Metadata', {
            'fields': ('executed_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MetricDefinition)
class MetricDefinitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'entity_type', 'calculation_type', 'is_active', 'is_system', 'created_at']
    list_filter = ['entity_type', 'calculation_type', 'is_active', 'is_system']
    search_fields = ['name', 'slug', 'description']
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Metric Information', {
            'fields': ('name', 'slug', 'description', 'entity_type', 'is_active', 'is_system')
        }),
        ('Calculation', {
            'fields': ('calculation_type', 'field_name', 'custom_formula')
        }),
        ('Formatting', {
            'fields': ('format_string', 'unit')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
