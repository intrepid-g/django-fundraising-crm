from ninja import NinjaAPI
from donors.api import router as donors_router
from donations.api import router as donations_router
from events.api import router as events_router
from communications.api import router as communications_router
from reports.api import router as reports_router


# Main API instance
api = NinjaAPI(
    title="Fundraising CRM API",
    version="1.0.0",
    description="Production-ready fundraising CRM API with donor management, donation tracking, campaigns, events, communications, and reporting."
)


# Register sub-routers
api.add_router("/donors/", donors_router)
api.add_router("/donations/", donations_router)
api.add_router("/events/", events_router)
api.add_router("/communications/", communications_router)
api.add_router("/reports/", reports_router)


# Health check endpoint
@api.get("/health")
def health_check(request):
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@api.get("/")
def api_root(request):
    """API root with available endpoints."""
    return {
        "name": "Fundraising CRM API",
        "version": "1.0.0",
        "endpoints": {
            "donors": {
                "list": "GET /api/donors/",
                "get": "GET /api/donors/{id}",
                "create": "POST /api/donors/",
                "update": "PUT /api/donors/{id}",
                "delete": "DELETE /api/donors/{id}",
                "search": "POST /api/donors/search",
                "stats": "GET /api/donors/{id}/stats",
                "tags": "POST/DELETE /api/donors/{id}/tags",
                "preferences": "GET/PUT /api/donors/{id}/preferences",
            },
            "donations": {
                "list": "GET /api/donations/",
                "get": "GET /api/donations/{id}",
                "create": "POST /api/donations/",
                "update": "PUT /api/donations/{id}",
                "complete": "POST /api/donations/{id}/complete",
                "recurring": "GET /api/donations/recurring",
                "summary": "GET /api/donations/stats/summary",
            },
            "campaigns": {
                "list": "GET /api/campaigns/",
                "get": "GET /api/campaigns/{id}",
                "create": "POST /api/campaigns/",
                "stats": "GET /api/campaigns/{id}/stats",
            },
            "events": {
                "list": "GET /api/events/",
                "upcoming": "GET /api/events/upcoming",
                "get": "GET /api/events/{id}",
                "create": "POST /api/events/",
                "update": "PUT /api/events/{id}",
                "delete": "DELETE /api/events/{id}",
                "stats": "GET /api/events/{id}/stats",
                "registrations": "GET/POST /api/events/{id}/registrations",
                "checkin": "POST /api/events/{id}/registrations/{id}/checkin",
                "sponsors": "GET/POST /api/events/{id}/sponsors",
                "tasks": "GET/POST/PUT/DELETE /api/events/{id}/tasks",
            },
            "communications": {
                "list": "GET /api/communications/",
                "get": "GET /api/communications/{id}",
                "create": "POST /api/communications/",
                "update": "PUT /api/communications/{id}",
                "followups": "GET /api/communications/followups",
                "complete_followup": "POST /api/communications/{id}/complete-followup",
                "templates": "GET/POST /api/communications/templates",
                "scheduled": "GET/POST /api/communications/scheduled",
                "stats": "GET /api/communications/stats/summary",
            },
            "reports": {
                "list": "GET /api/reports/",
                "get": "GET /api/reports/{id}",
                "create": "POST /api/reports/",
                "update": "PUT /api/reports/{id}",
                "delete": "DELETE /api/reports/{id}",
                "execute": "POST /api/reports/{id}/execute",
                "executions": "GET /api/reports/{id}/executions",
                "dashboards": "GET/POST /api/reports/dashboards",
                "metrics": "GET /api/reports/metrics",
                "overview": "GET /api/reports/stats/overview",
            },
        }
    }
