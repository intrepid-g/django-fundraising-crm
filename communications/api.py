from ninja import Router, Schema, ModelSchema
from datetime import datetime
from typing import List, Optional
from django.utils import timezone
from django.db import models
from .models import (
    Communication, CommunicationTemplate, CommunicationSchedule,
    CommunicationPreference, CallLog
)


router = Router()


# Schemas
class CommunicationSchema(ModelSchema):
    class Meta:
        model = Communication
        fields = [
            'id', 'communication_type', 'direction', 'status',
            'subject', 'content', 'summary',
            'from_address', 'to_address',
            'communication_date', 'scheduled_date', 'sent_date', 'delivered_date', 'read_date',
            'requires_followup', 'followup_date', 'followup_completed',
            'sentiment', 'outcome',
            'attachments', 'external_id', 'thread_id',
            'created_at', 'updated_at'
        ]


class CommunicationCreateSchema(Schema):
    donor_id: int
    communication_type: str
    direction: str = Communication.OUTBOUND
    subject: str = ""
    content: str = ""
    summary: str = ""
    from_address: str = ""
    to_address: str = ""
    communication_date: Optional[datetime] = None
    scheduled_date: Optional[datetime] = None
    requires_followup: bool = False
    followup_date: Optional[datetime] = None
    sentiment: str = ""
    outcome: str = ""
    related_donation_id: Optional[int] = None
    related_event_id: Optional[int] = None
    attachments: List[str] = []


class CommunicationUpdateSchema(Schema):
    communication_type: Optional[str] = None
    direction: Optional[str] = None
    status: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    communication_date: Optional[datetime] = None
    scheduled_date: Optional[datetime] = None
    requires_followup: Optional[bool] = None
    followup_date: Optional[datetime] = None
    followup_completed: Optional[bool] = None
    sentiment: Optional[str] = None
    outcome: Optional[str] = None


class CommunicationTemplateSchema(ModelSchema):
    class Meta:
        model = CommunicationTemplate
        fields = [
            'id', 'name', 'template_type', 'subject_template', 'body_template',
            'category', 'is_active', 'usage_count', 'available_variables',
            'created_at', 'updated_at'
        ]


class CommunicationTemplateCreateSchema(Schema):
    name: str
    template_type: str
    subject_template: str = ""
    body_template: str
    category: str = ""
    available_variables: List[str] = []


class CommunicationScheduleSchema(ModelSchema):
    class Meta:
        model = CommunicationSchedule
        fields = [
            'id', 'scheduled_date', 'status', 'subject', 'content',
            'template_context', 'is_automated', 'automation_trigger',
            'sent_date', 'error_message', 'created_at'
        ]


class CommunicationScheduleCreateSchema(Schema):
    donor_id: int
    template_id: Optional[int] = None
    scheduled_date: datetime
    subject: str = ""
    content: str = ""
    template_context: dict = {}
    is_automated: bool = False
    automation_trigger: str = ""


class CommunicationPreferenceSchema(ModelSchema):
    class Meta:
        model = CommunicationPreference
        fields = [
            'id', 'email_opt_in', 'phone_opt_in', 'sms_opt_in', 'mail_opt_in',
            'preferred_frequency', 'preferred_topics', 'exclude_topics',
            'preferred_contact_time', 'timezone',
            'do_not_contact', 'do_not_contact_reason', 'do_not_contact_until',
            'created_at', 'updated_at'
        ]


class CallLogSchema(ModelSchema):
    class Meta:
        model = CallLog
        fields = [
            'id', 'phone_number', 'duration_seconds', 'was_answered',
            'went_to_voicemail', 'call_quality', 'recording_url',
            'call_outcome', 'follow_up_required', 'follow_up_notes',
            'created_at'
        ]


class CallLogCreateSchema(Schema):
    communication_id: int
    phone_number: str
    duration_seconds: int = 0
    was_answered: bool = False
    went_to_voicemail: bool = False
    call_quality: str = ""
    recording_url: str = ""
    call_outcome: str = ""
    follow_up_required: bool = False
    follow_up_notes: str = ""


# Communication Endpoints
@router.get("/", response=List[CommunicationSchema])
def list_communications(
    request,
    donor_id: Optional[int] = None,
    communication_type: Optional[str] = None,
    status: Optional[str] = None,
    requires_followup: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0
):
    """List all communications with optional filtering."""
    queryset = Communication.objects.all()
    if donor_id:
        queryset = queryset.filter(donor_id=donor_id)
    if communication_type:
        queryset = queryset.filter(communication_type=communication_type)
    if status:
        queryset = queryset.filter(status=status)
    if requires_followup is not None:
        queryset = queryset.filter(requires_followup=requires_followup)
    return queryset[offset:offset+limit]


@router.get("/{communication_id}", response=CommunicationSchema)
def get_communication(request, communication_id: int):
    """Get a specific communication by ID."""
    return Communication.objects.get(id=communication_id)


@router.post("/", response=CommunicationSchema)
def create_communication(request, payload: CommunicationCreateSchema):
    """Create a new communication record."""
    from donors.models import Donor
    from donations.models import Donation
    from events.models import Event
    
    donor = Donor.objects.get(id=payload.donor_id)
    data = payload.dict()
    data['donor'] = donor
    
    # Set default communication date if not provided
    if not data.get('communication_date'):
        data['communication_date'] = timezone.now()
    
    # Handle related records
    if data.get('related_donation_id'):
        data['related_donation'] = Donation.objects.get(id=data.pop('related_donation_id'))
    else:
        data.pop('related_donation_id', None)
    
    if data.get('related_event_id'):
        data['related_event'] = Event.objects.get(id=data.pop('related_event_id'))
    else:
        data.pop('related_event_id', None)
    
    communication = Communication.objects.create(**data)
    return communication


@router.put("/{communication_id}", response=CommunicationSchema)
def update_communication(request, communication_id: int, payload: CommunicationUpdateSchema):
    """Update an existing communication."""
    communication = Communication.objects.get(id=communication_id)
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(communication, key, value)
    communication.save()
    return communication


@router.get("/followups", response=List[CommunicationSchema])
def list_followups(request, overdue_only: bool = False, limit: int = 50):
    """List communications requiring follow-up."""
    queryset = Communication.objects.filter(
        requires_followup=True,
        followup_completed=False
    )
    if overdue_only:
        queryset = queryset.filter(followup_date__lt=timezone.now())
    return queryset[:limit]


@router.post("/{communication_id}/complete-followup")
def complete_followup(request, communication_id: int):
    """Mark a follow-up as completed."""
    communication = Communication.objects.get(id=communication_id)
    communication.followup_completed = True
    communication.save()
    return {"success": True, "followup_completed": True}


# Template Endpoints
@router.get("/templates", response=List[CommunicationTemplateSchema])
def list_templates(request, template_type: Optional[str] = None, category: Optional[str] = None):
    """List all communication templates."""
    queryset = CommunicationTemplate.objects.filter(is_active=True)
    if template_type:
        queryset = queryset.filter(template_type=template_type)
    if category:
        queryset = queryset.filter(category=category)
    return queryset


@router.get("/templates/{template_id}", response=CommunicationTemplateSchema)
def get_template(request, template_id: int):
    """Get a specific template."""
    return CommunicationTemplate.objects.get(id=template_id)


@router.post("/templates", response=CommunicationTemplateSchema)
def create_template(request, payload: CommunicationTemplateCreateSchema):
    """Create a new communication template."""
    template = CommunicationTemplate.objects.create(**payload.dict())
    return template


@router.post("/templates/{template_id}/render")
def render_template(request, template_id: int, context: dict):
    """Render a template with given context."""
    template = CommunicationTemplate.objects.get(id=template_id)
    return template.render(context)


# Schedule Endpoints
@router.get("/scheduled", response=List[CommunicationScheduleSchema])
def list_scheduled(request, donor_id: Optional[int] = None, status: Optional[str] = None):
    """List scheduled communications."""
    queryset = CommunicationSchedule.objects.all()
    if donor_id:
        queryset = queryset.filter(donor_id=donor_id)
    if status:
        queryset = queryset.filter(status=status)
    return queryset


@router.post("/scheduled", response=CommunicationScheduleSchema)
def schedule_communication(request, payload: CommunicationScheduleCreateSchema):
    """Schedule a communication."""
    from donors.models import Donor
    
    donor = Donor.objects.get(id=payload.donor_id)
    data = payload.dict()
    data['donor'] = donor
    
    if data.get('template_id'):
        data['template'] = CommunicationTemplate.objects.get(id=data.pop('template_id'))
    else:
        data.pop('template_id', None)
    
    schedule = CommunicationSchedule.objects.create(**data)
    return schedule


@router.delete("/scheduled/{schedule_id}")
def cancel_scheduled(request, schedule_id: int):
    """Cancel a scheduled communication."""
    schedule = CommunicationSchedule.objects.get(id=schedule_id)
    schedule.status = CommunicationSchedule.CANCELLED
    schedule.save()
    return {"success": True, "status": "cancelled"}


# Preference Endpoints
@router.get("/preferences/{donor_id}", response=CommunicationPreferenceSchema)
def get_preferences(request, donor_id: int):
    """Get communication preferences for a donor."""
    from donors.models import Donor
    
    donor = Donor.objects.get(id=donor_id)
    preference, created = CommunicationPreference.objects.get_or_create(donor=donor)
    return preference


@router.put("/preferences/{donor_id}", response=CommunicationPreferenceSchema)
def update_preferences(request, donor_id: int, payload: CommunicationPreferenceSchema):
    """Update communication preferences for a donor."""
    from donors.models import Donor
    
    donor = Donor.objects.get(id=donor_id)
    preference, created = CommunicationPreference.objects.get_or_create(donor=donor)
    
    for key, value in payload.dict(exclude_unset=True).items():
        if key not in ['id', 'created_at', 'updated_at']:
            setattr(preference, key, value)
    preference.save()
    return preference


# Call Log Endpoints
@router.get("/{communication_id}/call", response=CallLogSchema)
def get_call_log(request, communication_id: int):
    """Get call log details for a communication."""
    return CallLog.objects.get(communication_id=communication_id)


@router.post("/{communication_id}/call", response=CallLogSchema)
def create_call_log(request, communication_id: int, payload: CallLogCreateSchema):
    """Create a call log for a communication."""
    communication = Communication.objects.get(id=communication_id)
    
    call_log = CallLog.objects.create(
        communication=communication,
        **payload.dict(exclude={'communication_id'})
    )
    return call_log


# Stats Endpoint
@router.get("/stats/summary")
def get_communication_stats(request, donor_id: Optional[int] = None):
    """Get communication statistics."""
    from django.db.models import Count, Avg
    
    queryset = Communication.objects.all()
    if donor_id:
        queryset = queryset.filter(donor_id=donor_id)
    
    stats = {
        "total_communications": queryset.count(),
        "by_type": dict(queryset.values('communication_type').annotate(count=Count('id')).values_list('communication_type', 'count')),
        "by_status": dict(queryset.values('status').annotate(count=Count('id')).values_list('status', 'count')),
        "pending_followups": queryset.filter(requires_followup=True, followup_completed=False).count(),
        "scheduled_count": CommunicationSchedule.objects.filter(status=CommunicationSchedule.PENDING).count(),
    }
    
    return stats
