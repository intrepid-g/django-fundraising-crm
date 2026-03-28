from ninja import Router, Schema, ModelSchema
from datetime import date
from typing import List, Optional
from decimal import Decimal
from django.db import models
from donations.models import Campaign


router = Router()


# Schemas
class CampaignSchema(ModelSchema):
    class Meta:
        model = Campaign
        fields = ['id', 'name', 'description', 'goal_amount', 'start_date', 'end_date', 'is_active', 'created_at']


class CampaignCreateSchema(Schema):
    name: str
    description: str = ""
    goal_amount: Decimal
    start_date: date
    end_date: Optional[date] = None
    is_active: bool = True


# Campaign Endpoints
@router.get("/", response=List[CampaignSchema])
def list_campaigns(request, active_only: bool = False):
    """List all campaigns."""
    queryset = Campaign.objects.all()
    if active_only:
        queryset = queryset.filter(is_active=True)
    return queryset


@router.get("/{campaign_id}/", response=CampaignSchema)
def get_campaign(request, campaign_id: int):
    """Get a specific campaign."""
    return Campaign.objects.get(id=campaign_id)


@router.post("/", response=CampaignSchema)
def create_campaign(request, payload: CampaignCreateSchema):
    """Create a new campaign."""
    campaign = Campaign.objects.create(**payload.dict())
    return campaign


@router.get("/{campaign_id}/stats/")
def get_campaign_stats(request, campaign_id: int):
    """Get statistics for a campaign."""
    from donations.models import Donation
    campaign = Campaign.objects.get(id=campaign_id)
    donations = Donation.objects.filter(campaign=campaign, status=Donation.COMPLETED)
    
    total_raised = donations.aggregate(total=models.Sum('amount'))['total'] or 0
    donation_count = donations.count()
    
    return {
        "campaign_name": campaign.name,
        "goal_amount": float(campaign.goal_amount),
        "total_raised": float(total_raised),
        "donation_count": donation_count,
        "progress_percentage": float(total_raised / campaign.goal_amount * 100) if campaign.goal_amount > 0 else 0,
        "days_remaining": (campaign.end_date - date.today()).days if campaign.end_date else None,
    }
