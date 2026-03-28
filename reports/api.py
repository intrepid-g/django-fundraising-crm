from ninja import Router, Schema, ModelSchema
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from decimal import Decimal
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Min, Max, Q, F
from django.db.models.functions import TruncMonth
from .models import Report, Dashboard, ReportExecution, MetricDefinition


router = Router()


# Schemas
class ReportSchema(ModelSchema):
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'report_type', 'description',
            'filters', 'group_by', 'metrics', 'sort_order',
            'date_range_start', 'date_range_end', 'date_range_preset',
            'is_scheduled', 'schedule_frequency', 'schedule_day_of_week', 'schedule_day_of_month',
            'schedule_recipients', 'is_active', 'is_favorite',
            'created_at', 'updated_at', 'last_run_at'
        ]


class ReportCreateSchema(Schema):
    name: str
    report_type: str
    description: str = ""
    filters: Dict[str, Any] = {}
    group_by: List[str] = []
    metrics: List[str] = []
    sort_order: List[Dict[str, str]] = []
    date_range_preset: str = "last_30_days"
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
    is_scheduled: bool = False
    schedule_frequency: str = ""
    schedule_day_of_week: Optional[int] = None
    schedule_day_of_month: Optional[int] = None
    schedule_recipients: List[str] = []


class ReportUpdateSchema(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    group_by: Optional[List[str]] = None
    metrics: Optional[List[str]] = None
    sort_order: Optional[List[Dict[str, str]]] = None
    date_range_preset: Optional[str] = None
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
    is_scheduled: Optional[bool] = None
    is_favorite: Optional[bool] = None


class DashboardSchema(ModelSchema):
    class Meta:
        model = Dashboard
        fields = [
            'id', 'name', 'description', 'layout_config', 'widgets',
            'is_default', 'is_shared', 'is_active', 'created_at', 'updated_at'
        ]


class DashboardCreateSchema(Schema):
    name: str
    description: str = ""
    layout_config: Dict[str, Any] = {}
    widgets: List[Dict[str, Any]] = []
    is_default: bool = False
    is_shared: bool = False


class ReportExecutionSchema(ModelSchema):
    class Meta:
        model = ReportExecution
        fields = [
            'id', 'status', 'parameters', 'result_summary', 'row_count',
            'output_format', 'started_at', 'completed_at', 'execution_time_seconds',
            'error_message', 'created_at'
        ]


class MetricDefinitionSchema(ModelSchema):
    class Meta:
        model = MetricDefinition
        fields = [
            'id', 'name', 'slug', 'description', 'entity_type',
            'calculation_type', 'field_name', 'custom_formula',
            'format_string', 'unit', 'is_active', 'is_system',
            'created_at', 'updated_at'
        ]


class ReportResultSchema(Schema):
    report_id: int
    report_name: str
    executed_at: datetime
    date_range: Dict[str, Optional[str]]
    summary: Dict[str, Any]
    data: List[Dict[str, Any]]
    row_count: int


class DashboardWidgetSchema(Schema):
    widget_type: str
    title: str
    metric: str
    filters: Dict[str, Any] = {}
    chart_type: Optional[str] = None
    position: Dict[str, int] = {}


# Report Endpoints
@router.get("/", response=List[ReportSchema])
def list_reports(
    request,
    report_type: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    is_active: bool = True
):
    """List all saved reports."""
    queryset = Report.objects.filter(is_active=is_active)
    if report_type:
        queryset = queryset.filter(report_type=report_type)
    if is_favorite is not None:
        queryset = queryset.filter(is_favorite=is_favorite)
    return queryset


@router.get("/{report_id}", response=ReportSchema)
def get_report(request, report_id: int):
    """Get a specific report configuration."""
    return Report.objects.get(id=report_id)


@router.post("/", response=ReportSchema)
def create_report(request, payload: ReportCreateSchema):
    """Create a new saved report."""
    report = Report.objects.create(**payload.dict())
    return report


@router.put("/{report_id}", response=ReportSchema)
def update_report(request, report_id: int, payload: ReportUpdateSchema):
    """Update a saved report."""
    report = Report.objects.get(id=report_id)
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(report, key, value)
    report.save()
    return report


@router.delete("/{report_id}")
def delete_report(request, report_id: int):
    """Delete a saved report."""
    report = Report.objects.get(id=report_id)
    report.delete()
    return {"success": True}


# Report Execution Endpoints
@router.post("/{report_id}/execute")
def execute_report(
    request,
    report_id: int,
    date_range_start: Optional[date] = None,
    date_range_end: Optional[date] = None,
    output_format: str = "json"
):
    """Execute a report and return results."""
    from donors.models import Donor
    from donations.models import Donation, Campaign
    
    report = Report.objects.get(id=report_id)
    
    # Determine date range
    if date_range_start and date_range_end:
        start_date = date_range_start
        end_date = date_range_end
    else:
        start_date, end_date = get_date_range_from_preset(report.date_range_preset or 'last_30_days')
    
    # Execute based on report type
    if report.report_type == Report.DONOR_ANALYTICS:
        result = generate_donor_analytics(start_date, end_date, report.filters)
    elif report.report_type == Report.DONATION_SUMMARY:
        result = generate_donation_summary(start_date, end_date, report.filters)
    elif report.report_type == Report.CAMPAIGN_PERFORMANCE:
        result = generate_campaign_performance(start_date, end_date, report.filters)
    elif report.report_type == Report.LTV_ANALYSIS:
        result = generate_ltv_analysis(report.filters)
    elif report.report_type == Report.RETENTION_ANALYSIS:
        result = generate_retention_analysis(start_date, end_date, report.filters)
    else:
        result = {"error": "Report type not implemented"}
    
    # Record execution
    execution = ReportExecution.objects.create(
        report=report,
        status=ReportExecution.COMPLETED,
        parameters={
            'date_range_start': str(start_date),
            'date_range_end': str(end_date),
        },
        result_data=result.get('data', []),
        result_summary=result.get('summary', {}),
        row_count=result.get('row_count', 0),
        output_format=output_format,
        started_at=timezone.now(),
        completed_at=timezone.now()
    )
    
    # Update last run
    report.last_run_at = timezone.now()
    report.save()
    
    return {
        "execution_id": execution.id,
        "report_id": report.id,
        "report_name": report.name,
        "date_range": {"start": str(start_date), "end": str(end_date)},
        "summary": result.get('summary', {}),
        "data": result.get('data', []),
        "row_count": result.get('row_count', 0)
    }


@router.get("/{report_id}/executions", response=List[ReportExecutionSchema])
def list_report_executions(request, report_id: int, limit: int = 10):
    """List recent executions of a report."""
    return ReportExecution.objects.filter(report_id=report_id).order_by('-created_at')[:limit]


# Dashboard Endpoints
@router.get("/dashboards/", response=List[DashboardSchema])
def list_dashboards(request, is_default: Optional[bool] = None):
    """List all dashboards."""
    queryset = Dashboard.objects.filter(is_active=True)
    if is_default is not None:
        queryset = queryset.filter(is_default=is_default)
    return queryset


@router.get("/dashboards/{dashboard_id}/", response=DashboardSchema)
def get_dashboard(request, dashboard_id: int):
    """Get a specific dashboard."""
    return Dashboard.objects.get(id=dashboard_id)


@router.post("/dashboards/", response=DashboardSchema)
def create_dashboard(request, payload: DashboardCreateSchema):
    """Create a new dashboard."""
    dashboard = Dashboard.objects.create(**payload.dict())
    return dashboard


@router.put("/dashboards/{dashboard_id}/", response=DashboardSchema)
def update_dashboard(request, dashboard_id: int, payload: DashboardCreateSchema):
    """Update a dashboard."""
    dashboard = Dashboard.objects.get(id=dashboard_id)
    for key, value in payload.dict().items():
        setattr(dashboard, key, value)
    dashboard.save()
    return dashboard


@router.delete("/dashboards/{dashboard_id}/")
def delete_dashboard(request, dashboard_id: int):
    """Delete a dashboard."""
    dashboard = Dashboard.objects.get(id=dashboard_id)
    dashboard.delete()
    return {"success": True}


@router.get("/dashboards/{dashboard_id}/data")
def get_dashboard_data(request, dashboard_id: int):
    """Get computed data for all widgets in a dashboard."""
    dashboard = Dashboard.objects.get(id=dashboard_id)
    
    widget_data = []
    for widget in dashboard.widgets:
        metric_data = compute_widget_data(widget)
        widget_data.append({
            "widget_id": widget.get('id'),
            "title": widget.get('title'),
            "data": metric_data
        })
    
    return {
        "dashboard_id": dashboard.id,
        "dashboard_name": dashboard.name,
        "widgets": widget_data
    }


# Metric Endpoints
@router.get("/metrics", response=List[MetricDefinitionSchema])
def list_metrics(request, entity_type: Optional[str] = None):
    """List available metrics."""
    queryset = MetricDefinition.objects.filter(is_active=True)
    if entity_type:
        queryset = queryset.filter(entity_type=entity_type)
    return queryset


@router.get("/metrics/{metric_slug}")
def get_metric_value(request, metric_slug: str, filters: Dict[str, Any] = {}):
    """Get current value for a specific metric."""
    metric = MetricDefinition.objects.get(slug=metric_slug)
    value = compute_metric(metric, filters)
    return {
        "metric": metric.name,
        "slug": metric.slug,
        "value": value,
        "unit": metric.unit,
        "formatted": metric.format_string.format(value=value)
    }


# Quick Stats Endpoints
@router.get("/stats/overview")
def get_overview_stats(request):
    """Get high-level CRM statistics."""
    from donors.models import Donor
    from donations.models import Donation
    from events.models import Event
    from communications.models import Communication
    
    today = timezone.now().date()
    thirty_days_ago = today - timezone.timedelta(days=30)
    
    # Donor stats
    total_donors = Donor.objects.count()
    new_donors_30d = Donor.objects.filter(created_at__date__gte=thirty_days_ago).count()
    
    # Donation stats
    total_donations = Donation.objects.filter(status='completed').count()
    total_raised = Donation.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    donations_30d = Donation.objects.filter(
        status='completed',
        donation_date__gte=thirty_days_ago
    )
    raised_30d = donations_30d.aggregate(total=Sum('amount'))['total'] or 0
    
    # Event stats
    upcoming_events = Event.objects.filter(
        start_date__gte=timezone.now(),
        status__in=['confirmed', 'planning']
    ).count()
    
    # Communication stats
    pending_followups = Communication.objects.filter(
        requires_followup=True,
        followup_completed=False
    ).count()
    
    return {
        "donors": {
            "total": total_donors,
            "new_30d": new_donors_30d,
        },
        "donations": {
            "total_count": total_donations,
            "total_amount": float(total_raised),
            "last_30d_count": donations_30d.count(),
            "last_30d_amount": float(raised_30d),
        },
        "events": {
            "upcoming": upcoming_events,
        },
        "communications": {
            "pending_followups": pending_followups,
        }
    }


# Helper functions
def get_date_range_from_preset(preset: str) -> tuple:
    """Convert preset to date range."""
    from datetime import timedelta
    
    today = timezone.now().date()
    
    presets = {
        'today': (today, today),
        'yesterday': (today - timedelta(days=1), today - timedelta(days=1)),
        'this_week': (today - timedelta(days=today.weekday()), today),
        'last_week': (today - timedelta(days=today.weekday() + 7), today - timedelta(days=today.weekday() + 1)),
        'this_month': (today.replace(day=1), today),
        'last_30_days': (today - timedelta(days=30), today),
        'last_90_days': (today - timedelta(days=90), today),
        'this_year': (today.replace(month=1, day=1), today),
        'all_time': (date(2000, 1, 1), today),
    }
    
    return presets.get(preset, presets['last_30_days'])


def generate_donor_analytics(start_date: date, end_date: date, filters: dict) -> dict:
    """Generate donor analytics report."""
    from donors.models import Donor
    from donations.models import Donation
    
    # Base queryset
    donors = Donor.objects.all()
    
    # Apply filters
    if filters.get('donor_type'):
        donors = donors.filter(donor_type=filters['donor_type'])
    if filters.get('tags'):
        donors = donors.filter(tags__overlap=filters['tags'])
    
    # Calculate metrics
    total_donors = donors.count()
    
    # New donors in period
    new_donors = donors.filter(created_at__date__range=(start_date, end_date)).count()
    
    # Active donors (made donation in period)
    active_donors = donors.filter(
        donations__donation_date__range=(start_date, end_date),
        donations__status='completed'
    ).distinct().count()
    
    # Lapsed donors (no donation in period, but had previous donation)
    lapsed_donors = donors.filter(
        last_donation_date__lt=start_date
    ).exclude(
        donations__donation_date__range=(start_date, end_date)
    ).count()
    
    # By type
    by_type = list(donors.values('donor_type').annotate(count=Count('id')).order_by('-count'))
    
    # Top donors by total donations
    top_donors = list(donors.order_by('-total_donations')[:10].values(
        'id', 'first_name', 'last_name', 'email', 'total_donations', 'donation_count'
    ))
    
    return {
        "summary": {
            "total_donors": total_donors,
            "new_donors": new_donors,
            "active_donors": active_donors,
            "lapsed_donors": lapsed_donors,
        },
        "data": {
            "by_type": by_type,
            "top_donors": top_donors,
        },
        "row_count": total_donors
    }


def generate_donation_summary(start_date: date, end_date: date, filters: dict) -> dict:
    """Generate donation summary report."""
    from donations.models import Donation
    
    donations = Donation.objects.filter(
        donation_date__range=(start_date, end_date),
        status='completed'
    )
    
    if filters.get('donation_type'):
        donations = donations.filter(donation_type=filters['donation_type'])
    if filters.get('campaign_id'):
        donations = donations.filter(campaign_id=filters['campaign_id'])
    
    # Summary stats
    total_count = donations.count()
    total_amount = donations.aggregate(total=Sum('amount'))['total'] or 0
    avg_amount = donations.aggregate(avg=Avg('amount'))['avg'] or 0
    min_amount = donations.aggregate(min=Min('amount'))['min'] or 0
    max_amount = donations.aggregate(max=Max('amount'))['max'] or 0
    
    # By type
    by_type = list(donations.values('donation_type').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('-total'))
    
    # By month (database-agnostic using TruncMonth)
    by_month = list(donations.annotate(
        month=TruncMonth('donation_date')
    ).values('month').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('month'))
    
    return {
        "summary": {
            "total_count": total_count,
            "total_amount": float(total_amount),
            "average_amount": float(avg_amount),
            "min_amount": float(min_amount),
            "max_amount": float(max_amount),
        },
        "data": {
            "by_type": by_type,
            "by_month": by_month,
        },
        "row_count": total_count
    }


def generate_campaign_performance(start_date: date, end_date: date, filters: dict) -> dict:
    """Generate campaign performance report."""
    from donations.models import Campaign, Donation
    
    campaigns = Campaign.objects.filter(
        start_date__lte=end_date
    ).filter(
        Q(end_date__gte=start_date) | Q(end_date__isnull=True)
    )
    
    results = []
    for campaign in campaigns:
        donations = Donation.objects.filter(
            campaign=campaign,
            status='completed',
            donation_date__range=(start_date, end_date)
        )
        
        total_raised = donations.aggregate(total=Sum('amount'))['total'] or 0
        donor_count = donations.values('donor').distinct().count()
        
        goal_percentage = 0
        if campaign.goal_amount > 0:
            goal_percentage = (float(total_raised) / float(campaign.goal_amount)) * 100
        
        results.append({
            "campaign_id": campaign.id,
            "campaign_name": campaign.name,
            "goal_amount": float(campaign.goal_amount),
            "total_raised": float(total_raised),
            "goal_percentage": round(goal_percentage, 2),
            "donor_count": donor_count,
            "donation_count": donations.count(),
            "is_active": campaign.is_active,
        })
    
    # Sort by total raised
    results.sort(key=lambda x: x['total_raised'], reverse=True)
    
    return {
        "summary": {
            "total_campaigns": len(results),
            "total_raised": sum(r['total_raised'] for r in results),
            "active_campaigns": sum(1 for r in results if r['is_active']),
        },
        "data": results,
        "row_count": len(results)
    }


def generate_ltv_analysis(filters: dict) -> dict:
    """Generate lifetime value analysis."""
    from donors.models import Donor
    from donations.models import Donation
    
    donors = Donor.objects.filter(donation_count__gt=0)
    
    # Calculate LTV tiers
    ltv_tiers = {
        'champion': {'min': 10000, 'count': 0, 'total': 0},
        'loyal': {'min': 1000, 'max': 9999, 'count': 0, 'total': 0},
        'potential': {'min': 100, 'max': 999, 'count': 0, 'total': 0},
        'new': {'min': 1, 'max': 99, 'count': 0, 'total': 0},
    }
    
    for donor in donors:
        total = float(donor.total_donations)
        
        if total >= 10000:
            ltv_tiers['champion']['count'] += 1
            ltv_tiers['champion']['total'] += total
        elif total >= 1000:
            ltv_tiers['loyal']['count'] += 1
            ltv_tiers['loyal']['total'] += total
        elif total >= 100:
            ltv_tiers['potential']['count'] += 1
            ltv_tiers['potential']['total'] += total
        else:
            ltv_tiers['new']['count'] += 1
            ltv_tiers['new']['total'] += total
    
    # Average LTV
    avg_ltv = donors.aggregate(avg=Avg('total_donations'))['avg'] or 0
    
    return {
        "summary": {
            "total_donors_with_donations": donors.count(),
            "average_ltv": float(avg_ltv),
        },
        "data": {
            "ltv_tiers": ltv_tiers,
        },
        "row_count": donors.count()
    }


def generate_retention_analysis(start_date: date, end_date: date, filters: dict) -> dict:
    """Generate donor retention analysis."""
    from donors.models import Donor
    from donations.models import Donation
    
    # Previous period
    period_length = (end_date - start_date).days
    prev_start = start_date - timezone.timedelta(days=period_length)
    prev_end = start_date - timezone.timedelta(days=1)
    
    # Donors who gave in previous period
    prev_donors = Donation.objects.filter(
        donation_date__range=(prev_start, prev_end),
        status='completed'
    ).values_list('donor_id', flat=True).distinct()
    
    # Of those, who gave again in current period
    retained_donors = Donation.objects.filter(
        donor_id__in=prev_donors,
        donation_date__range=(start_date, end_date),
        status='completed'
    ).values_list('donor_id', flat=True).distinct()
    
    prev_count = len(prev_donors)
    retained_count = len(retained_donors)
    
    retention_rate = (retained_count / prev_count * 100) if prev_count > 0 else 0
    
    return {
        "summary": {
            "previous_period_donors": prev_count,
            "retained_donors": retained_count,
            "retention_rate": round(retention_rate, 2),
            "churned_donors": prev_count - retained_count,
        },
        "data": {
            "period_comparison": {
                "previous": {"start": str(prev_start), "end": str(prev_end), "donors": prev_count},
                "current": {"start": str(start_date), "end": str(end_date), "donors": retained_count},
            }
        },
        "row_count": prev_count
    }


def compute_widget_data(widget: dict) -> dict:
    """Compute data for a dashboard widget."""
    # This is a simplified version - in production, this would be more sophisticated
    metric_slug = widget.get('metric')
    filters = widget.get('filters', {})
    
    # Get metric definition
    try:
        metric = MetricDefinition.objects.get(slug=metric_slug)
        value = compute_metric(metric, filters)
        return {
            "metric": metric.name,
            "value": value,
            "unit": metric.unit,
            "formatted": metric.format_string.format(value=value)
        }
    except MetricDefinition.DoesNotExist:
        return {"error": f"Metric {metric_slug} not found"}


def compute_metric(metric: MetricDefinition, filters: dict) -> Any:
    """Compute a single metric value."""
    from donors.models import Donor
    from donations.models import Donation
    
    # Determine base queryset
    if metric.entity_type == MetricDefinition.DONOR:
        queryset = Donor.objects.all()
    elif metric.entity_type == MetricDefinition.DONATION:
        queryset = Donation.objects.filter(status='completed')
    else:
        return None
    
    # Apply filters
    if filters.get('date_range'):
        date_range = filters['date_range']
        if metric.entity_type == MetricDefinition.DONATION:
            queryset = queryset.filter(donation_date__range=(date_range['start'], date_range['end']))
        elif metric.entity_type == MetricDefinition.DONOR:
            queryset = queryset.filter(created_at__date__range=(date_range['start'], date_range['end']))
    
    # Calculate
    if metric.calculation_type == 'count':
        return queryset.count()
    elif metric.calculation_type == 'sum':
        result = queryset.aggregate(total=Sum(metric.field_name))['total']
        return float(result) if result else 0
    elif metric.calculation_type == 'avg':
        result = queryset.aggregate(avg=Avg(metric.field_name))['avg']
        return float(result) if result else 0
    
    return None
