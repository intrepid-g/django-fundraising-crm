from ninja import Router, Schema, ModelSchema
from ninja.orm import create_schema
from datetime import datetime
from typing import List, Optional
from django.db import models
from .models import Donor


router = Router()


# Schemas
class DonorSchema(ModelSchema):
    class Meta:
        model = Donor
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'address_line1', 'address_line2', 'city', 'state', 
            'postal_code', 'country', 'donor_type', 'organization_name',
            'tags', 'segments', 'first_donation_date', 'last_donation_date',
            'total_donations', 'donation_count', 'email_opt_in',
            'notes', 'created_at', 'updated_at'
        ]


class DonorCreateSchema(Schema):
    first_name: str
    last_name: str
    email: str
    phone: str = ""
    donor_type: str = Donor.INDIVIDUAL
    organization_name: str = ""
    address_line1: str = ""
    address_line2: str = ""
    city: str = ""
    state: str = ""
    postal_code: str = ""
    country: str = "US"
    tags: List[str] = []
    segments: List[str] = []
    notes: str = ""
    email_opt_in: bool = True


class DonorUpdateSchema(Schema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    donor_type: Optional[str] = None
    organization_name: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    tags: Optional[List[str]] = None
    segments: Optional[List[str]] = None
    notes: Optional[str] = None
    email_opt_in: Optional[bool] = None


class DonorSearchSchema(Schema):
    query: str
    donor_type: Optional[str] = None
    tags: Optional[List[str]] = None
    min_donations: Optional[float] = None
    max_donations: Optional[float] = None


# Endpoints
@router.get("/", response=List[DonorSchema])
def list_donors(request, limit: int = 50, offset: int = 0):
    """List all donors with pagination."""
    return Donor.objects.all()[offset:offset+limit]


@router.get("/{donor_id}/", response=DonorSchema)
def get_donor(request, donor_id: int):
    """Get a specific donor by ID."""
    return Donor.objects.get(id=donor_id)


@router.post("/", response=DonorSchema)
def create_donor(request, payload: DonorCreateSchema):
    """Create a new donor."""
    donor = Donor.objects.create(**payload.dict())
    return donor


@router.put("/{donor_id}/", response=DonorSchema)
def update_donor(request, donor_id: int, payload: DonorUpdateSchema):
    """Update an existing donor."""
    donor = Donor.objects.get(id=donor_id)
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(donor, key, value)
    donor.save()
    return donor


@router.delete("/{donor_id}/")
def delete_donor(request, donor_id: int):
    """Delete a donor."""
    donor = Donor.objects.get(id=donor_id)
    donor.delete()
    return {"success": True}


@router.post("/search", response=List[DonorSchema])
def search_donors(request, payload: DonorSearchSchema):
    """Search donors by various criteria."""
    queryset = Donor.objects.all()
    
    # Text search
    if payload.query:
        queryset = queryset.filter(
            models.Q(first_name__icontains=payload.query) |
            models.Q(last_name__icontains=payload.query) |
            models.Q(email__icontains=payload.query) |
            models.Q(organization_name__icontains=payload.query)
        )
    
    # Filter by type
    if payload.donor_type:
        queryset = queryset.filter(donor_type=payload.donor_type)
    
    # Filter by donation amount
    if payload.min_donations is not None:
        queryset = queryset.filter(total_donations__gte=payload.min_donations)
    if payload.max_donations is not None:
        queryset = queryset.filter(total_donations__lte=payload.max_donations)
    
    # Filter by tags
    if payload.tags:
        for tag in payload.tags:
            queryset = queryset.filter(tags__contains=[tag])
    
    return queryset[:100]


@router.get("/{donor_id}/stats")
def get_donor_stats(request, donor_id: int):
    """Get donation statistics for a donor."""
    donor = Donor.objects.get(id=donor_id)
    return {
        "total_donations": float(donor.total_donations),
        "donation_count": donor.donation_count,
        "first_donation_date": donor.first_donation_date,
        "last_donation_date": donor.last_donation_date,
        "average_donation": float(donor.total_donations / donor.donation_count) if donor.donation_count > 0 else 0,
    }


@router.post("/{donor_id}/tags")
def add_donor_tags(request, donor_id: int, tags: List[str]):
    """Add tags to a donor."""
    donor = Donor.objects.get(id=donor_id)
    current_tags = set(donor.tags)
    current_tags.update(tags)
    donor.tags = list(current_tags)
    donor.save()
    return {"success": True, "tags": donor.tags}


@router.delete("/{donor_id}/tags")
def remove_donor_tags(request, donor_id: int, tags: List[str]):
    """Remove tags from a donor."""
    donor = Donor.objects.get(id=donor_id)
    current_tags = set(donor.tags)
    current_tags.difference_update(tags)
    donor.tags = list(current_tags)
    donor.save()
    return {"success": True, "tags": donor.tags}
