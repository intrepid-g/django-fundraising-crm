from ninja import Router, Schema, ModelSchema
from datetime import datetime, date
from typing import List, Optional
from decimal import Decimal
from django.db import models
from .models import Donation, Campaign


router = Router()


# Schemas
class CampaignSchema(ModelSchema):
    class Config:
        model = Campaign
        model_fields = ['id', 'name', 'description', 'goal_amount', 'start_date', 'end_date', 'is_active', 'created_at']


class CampaignCreateSchema(Schema):
    name: str
    description: str = ""
    goal_amount: Decimal
    start_date: date
    end_date: Optional[date] = None
    is_active: bool = True


class DonationSchema(ModelSchema):
    donor_name: str
    campaign_name: Optional[str] = None
    
    class Config:
        model = Donation
        model_fields = [
            'id', 'amount', 'donation_type', 'frequency', 'status',
            'donation_date', 'received_date', 'payment_method',
            'payment_reference', 'notes', 'is_anonymous', 'is_tax_deductible',
            'is_tribute', 'tribute_type', 'tribute_honoree', 'tribute_message',
            'created_at', 'updated_at'
        ]
    
    @staticmethod
    def resolve_donor_name(obj):
        return str(obj.donor)
    
    @staticmethod
    def resolve_campaign_name(obj):
        return obj.campaign.name if obj.campaign else None


class DonationCreateSchema(Schema):
    donor_id: int
    campaign_id: Optional[int] = None
    amount: Decimal
    donation_type: str = Donation.ONE_TIME
    frequency: str = ""
    donation_date: date
    payment_method: str = ""
    payment_reference: str = ""
    notes: str = ""
    is_anonymous: bool = False
    is_tax_deductible: bool = True
    is_tribute: bool = False
    tribute_type: str = ""
    tribute_honoree: str = ""
    tribute_message: str = ""


class DonationUpdateSchema(Schema):
    amount: Optional[Decimal] = None
    donation_type: Optional[str] = None
    frequency: Optional[str] = None
    status: Optional[str] = None
    donation_date: Optional[date] = None
    received_date: Optional[date] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    notes: Optional[str] = None
    is_anonymous: Optional[bool] = None
    is_tax_deductible: Optional[bool] = None


# Campaign Endpoints
@router.get("/campaigns", response=List[CampaignSchema])
def list_campaigns(request, active_only: bool = False):
    """List all campaigns."""
    queryset = Campaign.objects.all()
    if active_only:
        queryset = queryset.filter(is_active=True)
    return queryset


@router.get("/campaigns/{campaign_id}", response=CampaignSchema)
def get_campaign(request, campaign_id: int):
    """Get a specific campaign."""
    return Campaign.objects.get(id=campaign_id)


@router.post("/campaigns", response=CampaignSchema)
def create_campaign(request, payload: CampaignCreateSchema):
    """Create a new campaign."""
    campaign = Campaign.objects.create(**payload.dict())
    return campaign


@router.get("/campaigns/{campaign_id}/stats")
def get_campaign_stats(request, campaign_id: int):
    """Get statistics for a campaign."""
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


# Donation Endpoints
@router.get("/donations", response=List[DonationSchema])
def list_donations(request, limit: int = 50, offset: int = 0, status: str = None):
    """List all donations with optional filtering."""
    queryset = Donation.objects.all()
    if status:
        queryset = queryset.filter(status=status)
    return queryset[offset:offset+limit]


@router.get("/donations/{donation_id}", response=DonationSchema)
def get_donation(request, donation_id: int):
    """Get a specific donation."""
    return Donation.objects.get(id=donation_id)


@router.post("/donations", response=DonationSchema)
def create_donation(request, payload: DonationCreateSchema):
    """Create a new donation."""
    from donors.models import Donor
    
    donor = Donor.objects.get(id=payload.donor_id)
    donation_data = payload.dict()
    donation_data.pop('donor_id')
    donation_data.pop('campaign_id')
    
    donation = Donation.objects.create(donor=donor, **donation_data)
    
    if payload.campaign_id:
        campaign = Campaign.objects.get(id=payload.campaign_id)
        donation.campaign = campaign
        donation.save()
    
    return donation


@router.put("/donations/{donation_id}", response=DonationSchema)
def update_donation(request, donation_id: int, payload: DonationUpdateSchema):
    """Update a donation."""
    donation = Donation.objects.get(id=donation_id)
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(donation, key, value)
    donation.save()
    return donation


@router.post("/donations/{donation_id}/complete")
def complete_donation(request, donation_id: int, received_date: date = None):
    """Mark a donation as completed."""
    donation = Donation.objects.get(id=donation_id)
    donation.status = Donation.COMPLETED
    donation.received_date = received_date or date.today()
    donation.save()
    return {"success": True, "donation_id": donation_id}


@router.get("/donations/recurring")
def list_recurring_donations(request):
    """List all active recurring donations."""
    donations = Donation.objects.filter(
        donation_type=Donation.RECURRING,
        status=Donation.COMPLETED
    ).order_by('donor', '-donation_date').distinct('donor')
    
    return [
        {
            "id": d.id,
            "donor": str(d.donor),
            "amount": float(d.amount),
            "frequency": d.get_frequency_display(),
            "last_donation": d.donation_date,
        }
        for d in donations
    ]


@router.get("/donations/stats/summary")
def get_donation_summary(request, start_date: date = None, end_date: date = None):
    """Get donation summary statistics."""
    queryset = Donation.objects.filter(status=Donation.COMPLETED)
    
    if start_date:
        queryset = queryset.filter(donation_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(donation_date__lte=end_date)
    
    total_amount = queryset.aggregate(total=models.Sum('amount'))['total'] or 0
    count = queryset.count()
    unique_donors = queryset.values('donor').distinct().count()
    
    # By donation type
    by_type = {}
    for donation_type in [Donation.ONE_TIME, Donation.RECURRING, Donation.PLEDGE]:
        by_type[donation_type] = {
            "count": queryset.filter(donation_type=donation_type).count(),
            "total": float(queryset.filter(donation_type=donation_type).aggregate(
                total=models.Sum('amount')
            )['total'] or 0),
        }
    
    return {
        "total_amount": float(total_amount),
        "donation_count": count,
        "unique_donors": unique_donors,
        "average_donation": float(total_amount / count) if count > 0 else 0,
        "by_type": by_type,
    }
