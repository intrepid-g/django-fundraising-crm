"""
Reports app model tests
Comprehensive unit tests for all report-related models
"""
import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from reports.models import Report, Dashboard, ReportExecution, MetricDefinition
from factories import (
    ReportFactory, DashboardFactory, ReportExecutionFactory, MetricDefinitionFactory
)


# =============================================================================
# REPORT MODEL TESTS
# =============================================================================

@pytest.mark.django_db
class TestReportModel:
    """Test cases for the Report model"""
    
    def test_create_report_with_valid_data(self):
        """Test creating a report with valid data"""
        report = ReportFactory(
            name='Monthly Donations',
            report_type='donation_analysis',
            description='Analysis of monthly donation trends'
        )
        
        assert report.id is not None
        assert report.name == 'Monthly Donations'
        assert report.report_type == 'donation_analysis'
    
    def test_report_str_representation(self):
        """Test the string representation of a report"""
        report = ReportFactory(name='Q1 Summary')
        assert 'Q1 Summary' in str(report)
    
    def test_report_type_choices(self):
        """Test report type choices"""
        for report_type in ['donor_summary', 'donation_analysis', 'event_report', 'campaign_report', 'custom']:
            report = ReportFactory(report_type=report_type)
            assert report.report_type == report_type
    
    def test_report_filters_field(self):
        """Test report filters field"""
        report = ReportFactory(
            filters={
                'date_from': '2024-01-01',
                'date_to': '2024-12-31',
                'status': 'completed'
            }
        )
        
        assert report.filters['date_from'] == '2024-01-01'
        assert report.filters['status'] == 'completed'
    
    def test_report_output_format_choices(self):
        """Test report output format choices"""
        for output_format in ['table', 'chart', 'csv', 'pdf']:
            report = ReportFactory(output_format=output_format)
            assert report.output_format == output_format
    
    def test_report_scheduling_fields(self):
        """Test report scheduling fields"""
        report = ReportFactory(
            is_scheduled=True,
            schedule_frequency='monthly'
        )
        
        assert report.is_scheduled is True
        assert report.schedule_frequency == 'monthly'
    
    def test_report_schedule_frequency_choices(self):
        """Test report schedule frequency choices"""
        for frequency in ['daily', 'weekly', 'monthly', 'quarterly']:
            report = ReportFactory(
                is_scheduled=True,
                schedule_frequency=frequency
            )
            assert report.schedule_frequency == frequency
    
    def test_report_created_by_field(self):
        """Test report created_by field"""
        report = ReportFactory(created_by='Admin User')
        assert report.created_by == 'Admin User'
    
    def test_report_is_active_flag(self):
        """Test report is_active flag"""
        active_report = ReportFactory(is_active=True)
        inactive_report = ReportFactory(is_active=False)
        
        assert active_report.is_active is True
        assert inactive_report.is_active is False
    
    def test_report_timestamps(self):
        """Test report timestamps"""
        report = ReportFactory()
        assert report.created_at is not None
        assert report.updated_at is not None
    
    def test_report_update_fields(self):
        """Test updating report fields"""
        report = ReportFactory(name='Old Name', description='Old description')
        
        report.name = 'New Name'
        report.description = 'New description'
        report.save()
        
        updated_report = Report.objects.get(id=report.id)
        assert updated_report.name == 'New Name'
        assert updated_report.description == 'New description'
    
    def test_report_delete(self):
        """Test deleting a report"""
        report = ReportFactory()
        report_id = report.id
        report.delete()
        
        with pytest.raises(Report.DoesNotExist):
            Report.objects.get(id=report_id)
    
    def test_report_unique_name(self):
        """Test that report names must be unique"""
        report1 = ReportFactory(name='UniqueReport')
        
        with pytest.raises(Exception):
            ReportFactory(name='UniqueReport')


# =============================================================================
# DASHBOARD MODEL TESTS
# =============================================================================

@pytest.mark.django_db
class TestDashboardModel:
    """Test cases for the Dashboard model"""
    
    def test_create_dashboard_with_valid_data(self):
        """Test creating a dashboard with valid data"""
        dashboard = DashboardFactory(
            name='Executive Dashboard',
            description='High-level metrics for executives'
        )
        
        assert dashboard.id is not None
        assert dashboard.name == 'Executive Dashboard'
    
    def test_dashboard_str_representation(self):
        """Test the string representation of a dashboard"""
        dashboard = DashboardFactory(name='Fundraising Overview')
        assert 'Fundraising Overview' in str(dashboard)
    
    def test_dashboard_widgets_field(self):
        """Test dashboard widgets configuration"""
        dashboard = DashboardFactory(
            widgets=[
                {'type': 'stat', 'metric': 'total_donors', 'position': 1},
                {'type': 'chart', 'metric': 'donations_over_time', 'position': 2},
                {'type': 'table', 'metric': 'recent_donations', 'position': 3}
            ]
        )
        
        assert len(dashboard.widgets) == 3
        assert dashboard.widgets[0]['type'] == 'stat'
        assert dashboard.widgets[1]['metric'] == 'donations_over_time'
    
    def test_dashboard_layout_choices(self):
        """Test dashboard layout choices"""
        for layout in ['grid', 'list', 'custom']:
            dashboard = DashboardFactory(layout=layout)
            assert dashboard.layout == layout
    
    def test_dashboard_sharing_fields(self):
        """Test dashboard sharing fields"""
        dashboard = DashboardFactory(
            is_shared=True,
            shared_with=['user1', 'user2', 'user3']
        )
        
        assert dashboard.is_shared is True
        assert 'user1' in dashboard.shared_with
        assert 'user2' in dashboard.shared_with
    
    def test_dashboard_created_by_field(self):
        """Test dashboard created_by field"""
        dashboard = DashboardFactory(created_by='Dashboard Creator')
        assert dashboard.created_by == 'Dashboard Creator'
    
    def test_dashboard_is_active_flag(self):
        """Test dashboard is_active flag"""
        active_dashboard = DashboardFactory(is_active=True)
        inactive_dashboard = DashboardFactory(is_active=False)
        
        assert active_dashboard.is_active is True
        assert inactive_dashboard.is_active is False
    
    def test_dashboard_timestamps(self):
        """Test dashboard timestamps"""
        dashboard = DashboardFactory()
        assert dashboard.created_at is not None
        assert dashboard.updated_at is not None
    
    def test_dashboard_update_fields(self):
        """Test updating dashboard fields"""
        dashboard = DashboardFactory(name='Old Dashboard')
        
        dashboard.name = 'New Dashboard'
        dashboard.widgets = [{'type': 'stat', 'metric': 'new_metric'}]
        dashboard.save()
        
        updated_dashboard = Dashboard.objects.get(id=dashboard.id)
        assert updated_dashboard.name == 'New Dashboard'
        assert len(updated_dashboard.widgets) == 1


# =============================================================================
# REPORT EXECUTION MODEL TESTS
# =============================================================================

@pytest.mark.django_db
class TestReportExecutionModel:
    """Test cases for the ReportExecution model"""
    
    def test_create_execution_with_valid_data(self):
        """Test creating a report execution with valid data"""
        report = ReportFactory()
        execution = ReportExecutionFactory(
            report=report,
            executed_by='Report User',
            status='completed'
        )
        
        assert execution.id is not None
        assert execution.report == report
        assert execution.status == 'completed'
    
    def test_execution_str_representation(self):
        """Test the string representation of an execution"""
        report = ReportFactory(name='Monthly Report')
        execution = ReportExecutionFactory(report=report)
        
        str_repr = str(execution)
        assert 'Monthly Report' in str_repr
    
    def test_execution_status_choices(self):
        """Test execution status choices"""
        report = ReportFactory()
        
        for status in ['running', 'completed', 'failed', 'cancelled']:
            execution = ReportExecutionFactory(report=report, status=status)
            assert execution.status == status
    
    def test_execution_timestamps(self):
        """Test execution timestamp fields"""
        report = ReportFactory()
        execution = ReportExecutionFactory(
            report=report,
            started_at='2024-01-15 10:00:00',
            completed_at='2024-01-15 10:05:00'
        )
        
        assert execution.started_at is not None
        assert execution.completed_at is not None
    
    def test_execution_results_fields(self):
        """Test execution results fields"""
        report = ReportFactory()
        execution = ReportExecutionFactory(
            report=report,
            row_count=150,
            result_data={'summary': {'total': 10000, 'count': 150}}
        )
        
        assert execution.row_count == 150
        assert execution.result_data['summary']['total'] == 10000
    
    def test_execution_error_message(self):
        """Test execution error message field"""
        report = ReportFactory()
        execution = ReportExecutionFactory(
            report=report,
            status='failed',
            error_message='Database connection timeout'
        )
        
        assert execution.error_message == 'Database connection timeout'
    
    def test_execution_cascade_delete_report(self):
        """Test that executions are deleted when report is deleted"""
        report = ReportFactory()
        execution = ReportExecutionFactory(report=report)
        execution_id = execution.id
        
        report.delete()
        
        with pytest.raises(ReportExecution.DoesNotExist):
            ReportExecution.objects.get(id=execution_id)
    
    def test_report_multiple_executions(self):
        """Test a report with multiple executions"""
        report = ReportFactory()
        
        execution1 = ReportExecutionFactory(report=report, status='completed')
        execution2 = ReportExecutionFactory(report=report, status='completed')
        execution3 = ReportExecutionFactory(report=report, status='failed')
        
        assert report.executions.count() == 3
        assert report.executions.filter(status='completed').count() == 2
        assert report.executions.filter(status='failed').count() == 1


# =============================================================================
# METRIC DEFINITION MODEL TESTS
# =============================================================================

@pytest.mark.django_db
class TestMetricDefinitionModel:
    """Test cases for the MetricDefinition model"""
    
    def test_create_metric_with_valid_data(self):
        """Test creating a metric definition with valid data"""
        metric = MetricDefinitionFactory(
            name='Total Donations',
            description='Sum of all donation amounts',
            calculation_type='sum'
        )
        
        assert metric.id is not None
        assert metric.name == 'Total Donations'
        assert metric.calculation_type == 'sum'
    
    def test_metric_str_representation(self):
        """Test the string representation of a metric"""
        metric = MetricDefinitionFactory(name='Average Gift Size')
        assert 'Average Gift Size' in str(metric)
    
    def test_metric_calculation_type_choices(self):
        """Test metric calculation type choices"""
        for calc_type in ['sum', 'count', 'average', 'min', 'max', 'custom']:
            metric = MetricDefinitionFactory(calculation_type=calc_type)
            assert metric.calculation_type == calc_type
    
    def test_metric_formula_field(self):
        """Test metric formula field"""
        metric = MetricDefinitionFactory(
            calculation_type='custom',
            formula='SUM(amount) / COUNT(id)'
        )
        
        assert metric.formula == 'SUM(amount) / COUNT(id)'
    
    def test_metric_data_source_fields(self):
        """Test metric data source fields"""
        metric = MetricDefinitionFactory(
            model_name='Donation',
            field_name='amount'
        )
        
        assert metric.model_name == 'Donation'
        assert metric.field_name == 'amount'
    
    def test_metric_filters_field(self):
        """Test metric filters field"""
        metric = MetricDefinitionFactory(
            filters={
                'status': 'completed',
                'date_from': '2024-01-01'
            }
        )
        
        assert metric.filters['status'] == 'completed'
        assert metric.filters['date_from'] == '2024-01-01'
    
    def test_metric_display_format_choices(self):
        """Test metric display format choices"""
        for display_format in ['number', 'currency', 'percentage', 'date']:
            metric = MetricDefinitionFactory(display_format=display_format)
            assert metric.display_format == display_format
    
    def test_metric_is_active_flag(self):
        """Test metric is_active flag"""
        active_metric = MetricDefinitionFactory(is_active=True)
        inactive_metric = MetricDefinitionFactory(is_active=False)
        
        assert active_metric.is_active is True
        assert inactive_metric.is_active is False
    
    def test_metric_timestamps(self):
        """Test metric timestamps"""
        metric = MetricDefinitionFactory()
        assert metric.created_at is not None
        assert metric.updated_at is not None
    
    def test_metric_unique_name(self):
        """Test that metric names must be unique"""
        metric1 = MetricDefinitionFactory(name='UniqueMetric')
        
        with pytest.raises(Exception):
            MetricDefinitionFactory(name='UniqueMetric')


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

@pytest.mark.django_db
class TestReportsIntegration:
    """Integration tests for report-related functionality"""
    
    def test_report_with_multiple_executions(self):
        """Test a report with multiple execution history"""
        report = ReportFactory(name='Monthly Summary')
        
        # Create execution history
        execution1 = ReportExecutionFactory(
            report=report,
            status='completed',
            row_count=100,
            started_at='2024-01-01 10:00:00',
            completed_at='2024-01-01 10:02:00'
        )
        execution2 = ReportExecutionFactory(
            report=report,
            status='completed',
            row_count=105,
            started_at='2024-02-01 10:00:00',
            completed_at='2024-02-01 10:03:00'
        )
        execution3 = ReportExecutionFactory(
            report=report,
            status='failed',
            error_message='Timeout error'
        )
        
        assert report.executions.count() == 3
        assert report.executions.filter(status='completed').count() == 2
    
    def test_dashboard_with_multiple_widgets(self):
        """Test a dashboard with various widget types"""
        dashboard = DashboardFactory(
            name='Comprehensive Dashboard',
            widgets=[
                {'type': 'stat', 'metric': 'total_donors', 'title': 'Total Donors'},
                {'type': 'stat', 'metric': 'total_donations', 'title': 'Total Donations'},
                {'type': 'chart', 'metric': 'donations_by_month', 'chart_type': 'line'},
                {'type': 'chart', 'metric': 'donors_by_type', 'chart_type': 'pie'},
                {'type': 'table', 'metric': 'top_donors', 'limit': 10},
                {'type': 'table', 'metric': 'recent_events', 'limit': 5}
            ]
        )
        
        assert len(dashboard.widgets) == 6
        
        stat_widgets = [w for w in dashboard.widgets if w['type'] == 'stat']
        chart_widgets = [w for w in dashboard.widgets if w['type'] == 'chart']
        table_widgets = [w for w in dashboard.widgets if w['type'] == 'table']
        
        assert len(stat_widgets) == 2
        assert len(chart_widgets) == 2
        assert len(table_widgets) == 2
    
    def test_metrics_for_dashboard(self):
        """Test creating metrics for use in dashboards"""
        # Create various metrics
        total_donations = MetricDefinitionFactory(
            name='Total Donations',
            calculation_type='sum',
            model_name='Donation',
            field_name='amount',
            display_format='currency'
        )
        
        avg_donation = MetricDefinitionFactory(
            name='Average Donation',
            calculation_type='average',
            model_name='Donation',
            field_name='amount',
            display_format='currency'
        )
        
        donor_count = MetricDefinitionFactory(
            name='Donor Count',
            calculation_type='count',
            model_name='Donor',
            field_name='id',
            display_format='number'
        )
        
        # Use in dashboard
        dashboard = DashboardFactory(
            name='Key Metrics',
            widgets=[
                {'type': 'stat', 'metric': 'Total Donations'},
                {'type': 'stat', 'metric': 'Average Donation'},
                {'type': 'stat', 'metric': 'Donor Count'}
            ]
        )
        
        assert MetricDefinition.objects.filter(is_active=True).count() >= 3
        assert dashboard.widgets[0]['metric'] == 'Total Donations'
    
    def test_scheduled_report_workflow(self):
        """Test scheduled report execution workflow"""
        # Create scheduled report
        report = ReportFactory(
            name='Weekly Summary',
            is_scheduled=True,
            schedule_frequency='weekly'
        )
        
        # Simulate scheduled execution
        execution = ReportExecutionFactory(
            report=report,
            status='completed',
            executed_by='scheduler',
            row_count=500
        )
        
        assert report.is_scheduled is True
        assert report.schedule_frequency == 'weekly'
        assert execution.status == 'completed'
        assert execution.executed_by == 'scheduler'
    
    def test_report_with_complex_filters(self):
        """Test report with complex filter configuration"""
        report = ReportFactory(
            name='Major Donors Report',
            report_type='donor_summary',
            filters={
                'date_from': '2024-01-01',
                'date_to': '2024-12-31',
                'min_amount': 1000,
                'donor_types': ['individual', 'corporate'],
                'status': 'active',
                'tags': ['major_donor', 'vip']
            }
        )
        
        assert 'min_amount' in report.filters
        assert 'donor_types' in report.filters
        assert report.filters['min_amount'] == 1000
    
    def test_dashboard_sharing_workflow(self):
        """Test dashboard sharing workflow"""
        dashboard = DashboardFactory(
            name='Team Dashboard',
            is_shared=False
        )
        
        # Initially not shared
        assert dashboard.is_shared is False
        
        # Share with team
        dashboard.is_shared = True
        dashboard.shared_with = ['user1', 'user2', 'user3']
        dashboard.save()
        
        shared_dashboard = Dashboard.objects.get(id=dashboard.id)
        assert shared_dashboard.is_shared is True
        assert len(shared_dashboard.shared_with) == 3
