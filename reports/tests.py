"""
Unit tests for Reports app.
"""
import pytest
from decimal import Decimal
from datetime import datetime, date, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from donors.models import Donor
from donations.models import Donation, Campaign
from reports.models import Report, Dashboard, ReportExecution, MetricDefinition


class ReportModelTests(TestCase):
    """Test Report model functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="analyst",
            password="testpass123"
        )
        self.report = Report.objects.create(
            name="Monthly Donation Summary",
            report_type=Report.DONATION_SUMMARY,
            description="Summary of donations for the month",
            created_by=self.user,
            filters={"date_range": "last_30_days"},
            metrics=["total_amount", "total_count", "average_amount"],
            is_active=True
        )
    
    def test_report_creation(self):
        """Test basic report creation."""
        self.assertEqual(self.report.name, "Monthly Donation Summary")
        self.assertEqual(self.report.report_type, Report.DONATION_SUMMARY)
        self.assertTrue(self.report.is_active)
    
    def test_report_types(self):
        """Test different report types."""
        types = [
            Report.DONOR_ANALYTICS,
            Report.DONATION_SUMMARY,
            Report.CAMPAIGN_PERFORMANCE,
            Report.LTV_ANALYSIS,
            Report.RETENTION_ANALYSIS,
            Report.CUSTOM,
        ]
        
        for i, report_type in enumerate(types):
            report = Report.objects.create(
                name=f"Report {i}",
                report_type=report_type,
                created_by=self.user
            )
            self.assertEqual(report.report_type, report_type)
    
    def test_report_filters(self):
        """Test report filter configuration."""
        filters = {
            "date_range": "last_90_days",
            "donor_type": "individual",
            "min_amount": 100
        }
        
        report = Report.objects.create(
            name="Filtered Report",
            report_type=Report.DONATION_SUMMARY,
            created_by=self.user,
            filters=filters
        )
        
        self.assertEqual(report.filters["date_range"], "last_90_days")
        self.assertEqual(report.filters["min_amount"], 100)
    
    def test_report_metrics(self):
        """Test report metric selection."""
        metrics = ["total_amount", "donor_count", "new_donors", "retention_rate"]
        
        report = Report.objects.create(
            name="Metrics Report",
            report_type=Report.DONOR_ANALYTICS,
            created_by=self.user,
            metrics=metrics
        )
        
        self.assertEqual(len(report.metrics), 4)
        self.assertIn("retention_rate", report.metrics)
    
    def test_scheduled_report(self):
        """Test scheduled report configuration."""
        report = Report.objects.create(
            name="Weekly Report",
            report_type=Report.DONATION_SUMMARY,
            created_by=self.user,
            is_scheduled=True,
            schedule_frequency=Report.WEEKLY,
            schedule_day_of_week=1,  # Monday
            schedule_recipients=["admin@example.com", "director@example.com"]
        )
        
        self.assertTrue(report.is_scheduled)
        self.assertEqual(report.schedule_frequency, Report.WEEKLY)
        self.assertEqual(len(report.schedule_recipients), 2)
    
    def test_report_favorites(self):
        """Test report favoriting."""
        self.report.is_favorite = True
        self.report.save()
        
        favorites = Report.objects.filter(is_favorite=True)
        self.assertIn(self.report, favorites)


class DashboardModelTests(TestCase):
    """Test Dashboard model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="dashboard_user",
            password="testpass123"
        )
        self.dashboard = Dashboard.objects.create(
            name="Executive Dashboard",
            description="High-level metrics for executives",
            created_by=self.user,
            layout_config={"columns": 3, "rows": 2},
            widgets=[
                {"type": "metric", "position": {"x": 0, "y": 0}},
                {"type": "chart", "position": {"x": 1, "y": 0}}
            ],
            is_default=True,
            is_shared=True
        )
    
    def test_dashboard_creation(self):
        """Test dashboard creation."""
        self.assertEqual(self.dashboard.name, "Executive Dashboard")
        self.assertTrue(self.dashboard.is_default)
        self.assertTrue(self.dashboard.is_shared)
    
    def test_dashboard_layout(self):
        """Test dashboard layout configuration."""
        self.assertEqual(self.dashboard.layout_config["columns"], 3)
        self.assertEqual(len(self.dashboard.widgets), 2)
    
    def test_widget_configuration(self):
        """Test widget setup."""
        metric_widget = self.dashboard.widgets[0]
        self.assertEqual(metric_widget["type"], "metric")
        self.assertEqual(metric_widget["position"]["x"], 0)
    
    def test_default_dashboard(self):
        """Test default dashboard setting."""
        # Only one default per user
        Dashboard.objects.create(
            name="Another Dashboard",
            created_by=self.user,
            is_default=False
        )
        
        default_dashboards = Dashboard.objects.filter(
            created_by=self.user,
            is_default=True
        )
        self.assertEqual(default_dashboards.count(), 1)


class ReportExecutionTests(TestCase):
    """Test ReportExecution model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="executor",
            password="testpass123"
        )
        self.report = Report.objects.create(
            name="Test Report",
            report_type=Report.DONATION_SUMMARY,
            created_by=self.user
        )
    
    def test_execution_creation(self):
        """Test report execution creation."""
        execution = ReportExecution.objects.create(
            report=self.report,
            status=ReportExecution.PENDING,
            parameters={"date_range": "last_30_days"},
            output_format="json"
        )
        
        self.assertEqual(execution.status, ReportExecution.PENDING)
        self.assertEqual(execution.output_format, "json")
    
    def test_execution_status_transitions(self):
        """Test execution status workflow."""
        execution = ReportExecution.objects.create(
            report=self.report,
            status=ReportExecution.PENDING
        )
        
        execution.status = ReportExecution.RUNNING
        execution.started_at = timezone.now()
        execution.save()
        self.assertEqual(execution.status, ReportExecution.RUNNING)
        
        execution.status = ReportExecution.COMPLETED
        execution.completed_at = timezone.now()
        execution.execution_time_seconds = 5.5
        execution.row_count = 150
        execution.save()
        
        self.assertEqual(execution.status, ReportExecution.COMPLETED)
        self.assertEqual(execution.execution_time_seconds, 5.5)
    
    def test_execution_failure(self):
        """Test failed execution handling."""
        execution = ReportExecution.objects.create(
            report=self.report,
            status=ReportExecution.FAILED,
            error_message="Database connection timeout",
            completed_at=timezone.now()
        )
        
        self.assertEqual(execution.status, ReportExecution.FAILED)
        self.assertIsNotNone(execution.error_message)


class MetricDefinitionTests(TestCase):
    """Test MetricDefinition model."""
    
    def test_metric_creation(self):
        """Test metric definition creation."""
        metric = MetricDefinition.objects.create(
            name="Total Donations",
            slug="total_donations",
            description="Sum of all donation amounts",
            entity_type="donation",
            calculation_type="sum",
            field_name="amount",
            format_string="${:,.2f}",
            unit="USD",
            is_active=True
        )
        
        self.assertEqual(metric.slug, "total_donations")
        self.assertEqual(metric.calculation_type, "sum")
    
    def test_custom_formula_metric(self):
        """Test metric with custom formula."""
        metric = MetricDefinition.objects.create(
            name="Average Donation",
            slug="avg_donation",
            calculation_type="custom",
            custom_formula="total_amount / total_count",
            format_string="${:,.2f}",
            is_active=True
        )
        
        self.assertEqual(metric.calculation_type, "custom")
        self.assertIsNotNone(metric.custom_formula)


class ReportCalculationTests(TestCase):
    """Test report calculations and aggregations."""
    
    def setUp(self):
        # Create test donors
        self.donor1 = Donor.objects.create(
            first_name="Donor1",
            last_name="Test",
            email="d1@example.com",
            total_donations=Decimal("500.00"),
            donation_count=2
        )
        self.donor2 = Donor.objects.create(
            first_name="Donor2",
            last_name="Test",
            email="d2@example.com",
            total_donations=Decimal("1500.00"),
            donation_count=5
        )
        self.donor3 = Donor.objects.create(
            first_name="Donor3",
            last_name="Test",
            email="d3@example.com",
            total_donations=Decimal("50.00"),
            donation_count=1
        )
        
        # Create donations
        for i, donor in enumerate([self.donor1, self.donor2, self.donor3], 1):
            Donation.objects.create(
                donor=donor,
                amount=donor.total_donations,
                donation_date=date.today() - timedelta(days=i * 10)
            )
    
    def test_donor_ltv_segments(self):
        """Test LTV segment calculation."""
        # Champions: $10,000+
        # Loyal: $1,000-$9,999
        # Potential: $100-$999
        # New: $1-$99
        
        champions = Donor.objects.filter(total_donations__gte=10000)
        loyal = Donor.objects.filter(
            total_donations__gte=1000,
            total_donations__lt=10000
        )
        potential = Donor.objects.filter(
            total_donations__gte=100,
            total_donations__lt=1000
        )
        new_donors = Donor.objects.filter(
            total_donations__gte=1,
            total_donations__lt=100
        )
        
        self.assertEqual(champions.count(), 0)
        self.assertIn(self.donor2, loyal)
        self.assertIn(self.donor1, potential)
        self.assertIn(self.donor3, new_donors)
    
    def test_donation_aggregations(self):
        """Test donation aggregation calculations."""
        total = Donation.objects.aggregate(
            total=Sum('amount')
        )['total']
        
        count = Donation.objects.aggregate(
            count=Count('id')
        )['count']
        
        average = Donation.objects.aggregate(
            avg=Avg('amount')
        )['avg']
        
        self.assertEqual(total, Decimal("2050.00"))
        self.assertEqual(count, 3)
        self.assertEqual(average, Decimal("683.33"))
    
    def test_retention_calculation(self):
        """Test donor retention rate calculation."""
        # Create a donor who gave twice (retained)
        retained_donor = Donor.objects.create(
            first_name="Retained",
            last_name="Donor",
            email="retained@example.com",
            donation_count=3
        )
        
        # Create a donor who gave once (not retained)
        one_time_donor = Donor.objects.create(
            first_name="OneTime",
            last_name="Donor",
            email="onetime@example.com",
            donation_count=1
        )
        
        # Calculate retention
        total_donors = Donor.objects.filter(donation_count__gt=0).count()
        retained_donors = Donor.objects.filter(donation_count__gt=1).count()
        
        retention_rate = (retained_donors / total_donors) * 100
        
        self.assertEqual(total_donors, 5)  # 3 from setUp + 2 new
        self.assertEqual(retained_donors, 2)  # donor1, donor2, retained_donor


class ReportAPITests(TestCase):
    """Test Reports API endpoints."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="api_user",
            password="testpass123"
        )
        self.report = Report.objects.create(
            name="API Report",
            report_type=Report.DONATION_SUMMARY,
            created_by=self.user
        )
    
    def test_list_reports(self):
        """Test GET /api/reports/."""
        response = self.client.get("/api/reports/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    def test_get_report(self):
        """Test GET /api/reports/{id}/."""
        response = self.client.get(f"/api/reports/{self.report.id}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "API Report")
    
    def test_create_report(self):
        """Test POST /api/reports/."""
        payload = {
            "name": "New Report",
            "report_type": "donor_analytics",
            "description": "Test report",
            "filters": {},
            "metrics": ["total_donations"]
        }
        response = self.client.post(
            "/api/reports/",
            data=payload,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
    
    def test_execute_report(self):
        """Test POST /api/reports/{id}/execute."""
        response = self.client.post(f"/api/reports/{self.report.id}/execute")
        self.assertEqual(response.status_code, 200)
    
    def test_list_dashboards(self):
        """Test GET /api/reports/dashboards."""
        response = self.client.get("/api/reports/dashboards")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    def test_stats_overview(self):
        """Test GET /api/reports/stats/overview."""
        response = self.client.get("/api/reports/stats/overview")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_donors", data)
        self.assertIn("total_donations", data)


class ReportEdgeCaseTests(TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="edge",
            password="testpass123"
        )
    
    def test_empty_report_execution(self):
        """Test executing report with no data."""
        report = Report.objects.create(
            name="Empty Report",
            report_type=Report.DONATION_SUMMARY,
            created_by=self.user
        )
        
        # Execute on empty database
        execution = ReportExecution.objects.create(
            report=report,
            status=ReportExecution.COMPLETED,
            row_count=0,
            result_summary={"total_amount": 0, "total_count": 0}
        )
        
        self.assertEqual(execution.row_count, 0)
    
    def test_very_long_report_name(self):
        """Test handling of very long report names."""
        long_name = "A" * 300
        
        with self.assertRaises(Exception):
            Report.objects.create(
                name=long_name,
                report_type=Report.CUSTOM,
                created_by=self.user
            )
    
    def test_complex_filter_configuration(self):
        """Test complex nested filters."""
        complex_filters = {
            "date_range": "custom",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "donor_types": ["individual", "organization"],
            "tags": ["major_donor"],
            "amount_range": {"min": 100, "max": 10000},
            "exclude_anonymous": True
        }
        
        report = Report.objects.create(
            name="Complex Filter Report",
            report_type=Report.DONATION_SUMMARY,
            created_by=self.user,
            filters=complex_filters
        )
        
        self.assertEqual(report.filters["amount_range"]["min"], 100)
        self.assertTrue(report.filters["exclude_anonymous"])
    
    def test_report_with_many_metrics(self):
        """Test report with many metrics."""
        many_metrics = [f"metric_{i}" for i in range(50)]
        
        report = Report.objects.create(
            name="Many Metrics Report",
            report_type=Report.CUSTOM,
            created_by=self.user,
            metrics=many_metrics
        )
        
        self.assertEqual(len(report.metrics), 50)
