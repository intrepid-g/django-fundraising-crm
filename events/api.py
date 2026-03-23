from ninja import Router, Schema, ModelSchema
from ninja.orm import create_schema
from datetime import datetime
from typing import List, Optional
from django.utils import timezone
from django.db import models
from .models import Event, EventRegistration, EventSponsor, EventTask


router = Router()


# Schemas
class EventSchema(ModelSchema):
    class Meta:
        model = Event
        fields = [
            'id', 'name', 'description', 'event_type', 'status',
            'start_date', 'end_date', 'setup_date',
            'venue_name', 'venue_address', 'venue_city', 'venue_state',
            'venue_postal_code', 'venue_country', 'virtual_event_url', 'is_virtual',
            'capacity', 'registration_deadline', 'requires_registration', 'is_invite_only',
            'fundraising_goal', 'ticket_price', 'sponsor_goal',
            'actual_attendees', 'total_raised', 'total_expenses',
            'notes', 'created_at', 'updated_at'
        ]


class EventCreateSchema(Schema):
    name: str
    description: str = ""
    event_type: str = Event.OTHER
    status: str = Event.DRAFT
    start_date: datetime
    end_date: Optional[datetime] = None
    setup_date: Optional[datetime] = None
    venue_name: str = ""
    venue_address: str = ""
    venue_city: str = ""
    venue_state: str = ""
    venue_postal_code: str = ""
    venue_country: str = "US"
    virtual_event_url: str = ""
    is_virtual: bool = False
    capacity: Optional[int] = None
    registration_deadline: Optional[datetime] = None
    requires_registration: bool = True
    is_invite_only: bool = False
    fundraising_goal: float = 0
    ticket_price: float = 0
    sponsor_goal: float = 0
    campaign_id: Optional[int] = None
    notes: str = ""


class EventUpdateSchema(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    setup_date: Optional[datetime] = None
    venue_name: Optional[str] = None
    venue_address: Optional[str] = None
    venue_city: Optional[str] = None
    venue_state: Optional[str] = None
    venue_postal_code: Optional[str] = None
    venue_country: Optional[str] = None
    virtual_event_url: Optional[str] = None
    is_virtual: Optional[bool] = None
    capacity: Optional[int] = None
    registration_deadline: Optional[datetime] = None
    requires_registration: Optional[bool] = None
    is_invite_only: Optional[bool] = None
    fundraising_goal: Optional[float] = None
    ticket_price: Optional[float] = None
    sponsor_goal: Optional[float] = None
    campaign_id: Optional[int] = None
    notes: Optional[str] = None


class EventRegistrationSchema(ModelSchema):
    class Meta:
        model = EventRegistration
        fields = [
            'id', 'status', 'number_of_guests', 'dietary_requirements',
            'special_requests', 'amount_paid', 'payment_method',
            'payment_reference', 'checked_in_at', 'registered_at'
        ]


class EventRegistrationCreateSchema(Schema):
    event_id: int
    donor_id: int
    number_of_guests: int = 1
    dietary_requirements: str = ""
    special_requests: str = ""
    amount_paid: float = 0
    payment_method: str = ""
    payment_reference: str = ""


class EventRegistrationUpdateSchema(Schema):
    status: Optional[str] = None
    number_of_guests: Optional[int] = None
    dietary_requirements: Optional[str] = None
    special_requests: Optional[str] = None
    amount_paid: Optional[float] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None


class EventSponsorSchema(ModelSchema):
    class Meta:
        model = EventSponsor
        fields = [
            'id', 'sponsor_name', 'level', 'amount', 'status',
            'benefits_description', 'logo_url', 'website_url',
            'notes', 'created_at', 'updated_at'
        ]


class EventSponsorCreateSchema(Schema):
    event_id: int
    sponsor_name: str
    sponsor_contact_id: Optional[int] = None
    level: str = EventSponsor.BRONZE
    amount: float = 0
    status: str = EventSponsor.PENDING
    benefits_description: str = ""
    logo_url: str = ""
    website_url: str = ""
    notes: str = ""


class EventTaskSchema(ModelSchema):
    class Meta:
        model = EventTask
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'due_date', 'completed_at', 'created_at', 'updated_at'
        ]


class EventTaskCreateSchema(Schema):
    event_id: int
    title: str
    description: str = ""
    status: str = EventTask.TODO
    priority: str = EventTask.MEDIUM
    assigned_to_id: Optional[int] = None
    due_date: Optional[datetime] = None


class EventTaskUpdateSchema(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to_id: Optional[int] = None
    due_date: Optional[datetime] = None


# Event Endpoints
@router.get("/events", response=List[EventSchema])
def list_events(request, status: Optional[str] = None, event_type: Optional[str] = None, limit: int = 50, offset: int = 0):
    """List all events with optional filtering."""
    queryset = Event.objects.all()
    if status:
        queryset = queryset.filter(status=status)
    if event_type:
        queryset = queryset.filter(event_type=event_type)
    return queryset[offset:offset+limit]


@router.get("/events/{event_id}", response=EventSchema)
def get_event(request, event_id: int):
    """Get a specific event by ID."""
    return Event.objects.get(id=event_id)


@router.get("/events/upcoming", response=List[EventSchema])
def list_upcoming_events(request, limit: int = 10):
    """List upcoming events."""
    now = timezone.now()
    return Event.objects.filter(
        start_date__gte=now,
        status__in=[Event.CONFIRMED, Event.PLANNING]
    ).order_by('start_date')[:limit]


@router.post("/events", response=EventSchema)
def create_event(request, payload: EventCreateSchema):
    """Create a new event."""
    data = payload.dict()
    if data.get('campaign_id'):
        from donations.models import Campaign
        data['campaign'] = Campaign.objects.get(id=data.pop('campaign_id'))
    else:
        data.pop('campaign_id', None)
    
    event = Event.objects.create(**data)
    return event


@router.put("/events/{event_id}", response=EventSchema)
def update_event(request, event_id: int, payload: EventUpdateSchema):
    """Update an existing event."""
    event = Event.objects.get(id=event_id)
    data = payload.dict(exclude_unset=True)
    
    if 'campaign_id' in data:
        if data['campaign_id']:
            from donations.models import Campaign
            data['campaign'] = Campaign.objects.get(id=data.pop('campaign_id'))
        else:
            data.pop('campaign_id')
            data['campaign'] = None
    
    for key, value in data.items():
        setattr(event, key, value)
    event.save()
    return event


@router.delete("/events/{event_id}")
def delete_event(request, event_id: int):
    """Delete an event."""
    event = Event.objects.get(id=event_id)
    event.delete()
    return {"success": True}


@router.get("/events/{event_id}/stats")
def get_event_stats(request, event_id: int):
    """Get event statistics."""
    event = Event.objects.get(id=event_id)
    return {
        "total_registrations": event.registrations.count(),
        "confirmed_attendees": event.registrations.filter(status=EventRegistration.CONFIRMED).count(),
        "actual_attendees": event.actual_attendees,
        "total_raised": float(event.total_raised),
        "fundraising_goal": float(event.fundraising_goal),
        "goal_percentage": (float(event.total_raised) / float(event.fundraising_goal) * 100) if event.fundraising_goal > 0 else 0,
        "sponsor_count": event.sponsors.count(),
        "sponsor_total": float(event.sponsors.aggregate(total=sum('amount'))['total'] or 0),
        "capacity_remaining": (event.capacity - event.actual_attendees) if event.capacity else None,
    }


# Event Registration Endpoints
@router.get("/events/{event_id}/registrations", response=List[EventRegistrationSchema])
def list_event_registrations(request, event_id: int, status: Optional[str] = None):
    """List all registrations for an event."""
    queryset = EventRegistration.objects.filter(event_id=event_id)
    if status:
        queryset = queryset.filter(status=status)
    return queryset


@router.post("/events/{event_id}/registrations", response=EventRegistrationSchema)
def create_event_registration(request, event_id: int, payload: EventRegistrationCreateSchema):
    """Register a donor for an event."""
    from donors.models import Donor
    
    event = Event.objects.get(id=event_id)
    donor = Donor.objects.get(id=payload.donor_id)
    
    registration = EventRegistration.objects.create(
        event=event,
        donor=donor,
        number_of_guests=payload.number_of_guests,
        dietary_requirements=payload.dietary_requirements,
        special_requests=payload.special_requests,
        amount_paid=payload.amount_paid,
        payment_method=payload.payment_method,
        payment_reference=payload.payment_reference
    )
    return registration


@router.put("/events/{event_id}/registrations/{registration_id}", response=EventRegistrationSchema)
def update_event_registration(request, event_id: int, registration_id: int, payload: EventRegistrationUpdateSchema):
    """Update an event registration."""
    registration = EventRegistration.objects.get(id=registration_id, event_id=event_id)
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(registration, key, value)
    registration.save()
    return registration


@router.post("/events/{event_id}/registrations/{registration_id}/checkin")
def checkin_registration(request, event_id: int, registration_id: int):
    """Check in a registration."""
    registration = EventRegistration.objects.get(id=registration_id, event_id=event_id)
    registration.status = EventRegistration.ATTENDED
    registration.checked_in_at = timezone.now()
    registration.save()
    return {"success": True, "checked_in_at": registration.checked_in_at}


# Event Sponsor Endpoints
@router.get("/events/{event_id}/sponsors", response=List[EventSponsorSchema])
def list_event_sponsors(request, event_id: int):
    """List all sponsors for an event."""
    return EventSponsor.objects.filter(event_id=event_id)


@router.post("/events/{event_id}/sponsors", response=EventSponsorSchema)
def create_event_sponsor(request, event_id: int, payload: EventSponsorCreateSchema):
    """Add a sponsor to an event."""
    from donors.models import Donor
    
    event = Event.objects.get(id=event_id)
    data = payload.dict()
    
    if data.get('sponsor_contact_id'):
        data['sponsor_contact'] = Donor.objects.get(id=data.pop('sponsor_contact_id'))
    else:
        data.pop('sponsor_contact_id', None)
    
    data['event'] = event
    sponsor = EventSponsor.objects.create(**data)
    return sponsor


# Event Task Endpoints
@router.get("/events/{event_id}/tasks", response=List[EventTaskSchema])
def list_event_tasks(request, event_id: int, status: Optional[str] = None):
    """List all tasks for an event."""
    queryset = EventTask.objects.filter(event_id=event_id)
    if status:
        queryset = queryset.filter(status=status)
    return queryset


@router.post("/events/{event_id}/tasks", response=EventTaskSchema)
def create_event_task(request, event_id: int, payload: EventTaskCreateSchema):
    """Create a task for an event."""
    from django.contrib.auth.models import User
    
    event = Event.objects.get(id=event_id)
    data = payload.dict()
    
    if data.get('assigned_to_id'):
        data['assigned_to'] = User.objects.get(id=data.pop('assigned_to_id'))
    else:
        data.pop('assigned_to_id', None)
    
    data['event'] = event
    task = EventTask.objects.create(**data)
    return task


@router.put("/events/{event_id}/tasks/{task_id}", response=EventTaskSchema)
def update_event_task(request, event_id: int, task_id: int, payload: EventTaskUpdateSchema):
    """Update an event task."""
    from django.contrib.auth.models import User
    
    task = EventTask.objects.get(id=task_id, event_id=event_id)
    data = payload.dict(exclude_unset=True)
    
    if 'assigned_to_id' in data:
        if data['assigned_to_id']:
            data['assigned_to'] = User.objects.get(id=data.pop('assigned_to_id'))
        else:
            data.pop('assigned_to_id')
            data['assigned_to'] = None
    
    # Mark completed if status changed to completed
    if data.get('status') == EventTask.COMPLETED and task.status != EventTask.COMPLETED:
        data['completed_at'] = timezone.now()
    
    for key, value in data.items():
        setattr(task, key, value)
    task.save()
    return task


@router.delete("/events/{event_id}/tasks/{task_id}")
def delete_event_task(request, event_id: int, task_id: int):
    """Delete an event task."""
    task = EventTask.objects.get(id=task_id, event_id=event_id)
    task.delete()
    return {"success": True}
