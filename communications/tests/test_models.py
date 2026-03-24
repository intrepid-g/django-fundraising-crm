"""
Communications app model tests
Comprehensive unit tests for all communication-related models
"""
import pytest
from django.core.exceptions import ValidationError
from communications.models import (
    Communication, CommunicationTemplate, CommunicationSchedule,
    CommunicationPreference, CallLog
)
from factories import (
    DonorFactory, CommunicationFactory, CommunicationTemplateFactory,
    CommunicationScheduleFactory, CommunicationPreferenceFactory, CallLogFactory
)


# =============================================================================
# COMMUNICATION MODEL TESTS
# =============================================================================

@pytest.mark.django_db
class TestCommunicationModel:
    """Test cases for the Communication model"""
    
    def test_create_communication_with_valid_data(self):
        """Test creating a communication with valid data"""
        donor = DonorFactory()
        communication = CommunicationFactory(
            donor=donor,
            communication_type='email',
            subject='Thank you for your donation',
            content='Dear donor, thank you for your generous support.'
        )
        
        assert communication.id is not None
        assert communication.donor == donor
        assert communication.communication_type == 'email'
        assert communication.subject == 'Thank you for your donation'
    
    def test_communication_str_representation(self):
        """Test the string representation of a communication"""
        donor = DonorFactory(first_name='John', last_name='Doe')
        communication = CommunicationFactory(
            donor=donor,
            communication_type='email',
            subject='Test Subject'
        )
        
        str_repr = str(communication)
        assert 'Test Subject' in str_repr or 'John Doe' in str_repr
    
    def test_communication_type_choices(self):
        """Test communication type choices"""
        donor = DonorFactory()
        
        for comm_type in ['email', 'phone', 'sms', 'meeting', 'note', 'mail']:
            communication = CommunicationFactory(
                donor=donor,
                communication_type=comm_type
            )
            assert communication.communication_type == comm_type
    
    def test_communication_direction_choices(self):
        """Test communication direction choices"""
        donor = DonorFactory()
        
        for direction in ['inbound', 'outbound']:
            communication = CommunicationFactory(
                donor=donor,
                direction=direction
            )
            assert communication.direction == direction
    
    def test_communication_status_choices(self):
        """Test communication status choices"""
        donor = DonorFactory()
        
        for status in ['draft', 'sent', 'delivered', 'read', 'failed']:
            communication = CommunicationFactory(
                donor=donor,
                status=status
            )
            assert communication.status == status
    
    def test_communication_status_workflow(self):
        """Test communication status workflow"""
        donor = DonorFactory()
        communication = CommunicationFactory(
            donor=donor,
            status='draft'
        )
        
        # Send the communication
        communication.status = 'sent'
        communication.sent_at = '2024-01-15 10:00:00'
        communication.save()
        
        sent_comm = Communication.objects.get(id=communication.id)
        assert sent_comm.status == 'sent'
        assert sent_comm.sent_at is not None
        
        # Mark as delivered
        communication.status = 'delivered'
        communication.save()
        assert Communication.objects.get(id=communication.id).status == 'delivered'
    
    def test_communication_content_field(self):
        """Test communication content field"""
        donor = DonorFactory()
        communication = CommunicationFactory(
            donor=donor,
            content='This is the body of the communication.'
        )
        
        assert communication.content == 'This is the body of the communication.'
    
    def test_communication_timestamps(self):
        """Test communication timestamp fields"""
        donor = DonorFactory()
        communication = CommunicationFactory(
            donor=donor,
            sent_at='2024-01-15 10:00:00',
            received_at='2024-01-15 10:05:00'
        )
        
        assert communication.sent_at is not None
        assert communication.received_at is not None
    
    def test_communication_follow_up_fields(self):
        """Test communication follow-up fields"""
        donor = DonorFactory()
        communication = CommunicationFactory(
            donor=donor,
            requires_follow_up=True,
            follow_up_date='2024-01-20'
        )
        
        assert communication.requires_follow_up is True
        assert communication.follow_up_date is not None
    
    def test_communication_campaign_tracking(self):
        """Test communication campaign tracking"""
        donor = DonorFactory()
        communication = CommunicationFactory(
            donor=donor,
            campaign='Spring2024'
        )
        
        assert communication.campaign == 'Spring2024'
    
    def test_communication_cascade_delete(self):
        """Test that communications are deleted when donor is deleted"""
        donor = DonorFactory()
        communication = CommunicationFactory(donor=donor)
        comm_id = communication.id
        
        donor.delete()
        
        with pytest.raises(Communication.DoesNotExist):
            Communication.objects.get(id=comm_id)
    
    def test_donor_multiple_communications(self):
        """Test a donor with multiple communications"""
        donor = DonorFactory()
        
        comm1 = CommunicationFactory(donor=donor, communication_type='email')
        comm2 = CommunicationFactory(donor=donor, communication_type='phone')
        comm3 = CommunicationFactory(donor=donor, communication_type='meeting')
        
        assert donor.communications.count() == 3


# =============================================================================
# COMMUNICATION TEMPLATE MODEL TESTS
# =============================================================================

@pytest.mark.django_db
class TestCommunicationTemplateModel:
    """Test cases for the CommunicationTemplate model"""
    
    def test_create_template_with_valid_data(self):
        """Test creating a template with valid data"""
        template = CommunicationTemplateFactory(
            name='Thank You Email',
            template_type='email',
            subject_template='Thank you {{donor_name}}!',
            body_template='Dear {{donor_name}}, thank you for your {{amount}} donation.'
        )
        
        assert template.id is not None
        assert template.name == 'Thank You Email'
        assert template.template_type == 'email'
    
    def test_template_str_representation(self):
        """Test the string representation of a template"""
        template = CommunicationTemplateFactory(name='Welcome Template')
        assert 'Welcome Template' in str(template)
    
    def test_template_type_choices(self):
        """Test template type choices"""
        for template_type in ['email', 'sms', 'letter']:
            template = CommunicationTemplateFactory(template_type=template_type)
            assert template.template_type == template_type
    
    def test_template_variable_substitution(self):
        """Test template variable substitution"""
        template = CommunicationTemplateFactory(
            subject_template='Hello {{donor_name}}',
            body_template='Thank you for {{amount}}',
            variables=['donor_name', 'amount']
        )
        
        # Simulate rendering
        context = {'donor_name': 'John Doe', 'amount': '$100'}
        rendered_subject = template.subject_template.replace('{{donor_name}}', context['donor_name'])
        rendered_body = template.body_template.replace('{{amount}}', context['amount'])
        
        assert rendered_subject == 'Hello John Doe'
        assert rendered_body == 'Thank you for $100'
    
    def test_template_variables_field(self):
        """Test template variables field"""
        template = CommunicationTemplateFactory(
            variables=['donor_name', 'amount', 'event_name', 'date']
        )
        
        assert 'donor_name' in template.variables
        assert 'amount' in template.variables
    
    def test_template_is_active_flag(self):
        """Test template is_active flag"""
        active_template = CommunicationTemplateFactory(is_active=True)
        inactive_template = CommunicationTemplateFactory(is_active=False)
        
        assert active_template.is_active is True
        assert inactive_template.is_active is False
    
    def test_template_usage_count(self):
        """Test template usage count tracking"""
        template = CommunicationTemplateFactory(usage_count=42)
        assert template.usage_count == 42
    
    def test_template_unique_name(self):
        """Test that template names must be unique"""
        template1 = CommunicationTemplateFactory(name='UniqueTemplate')
        
        with pytest.raises(Exception):
            CommunicationTemplateFactory(name='UniqueTemplate')


# =============================================================================
# COMMUNICATION SCHEDULE MODEL TESTS
# =============================================================================

@pytest.mark.django_db
class TestCommunicationScheduleModel:
    """Test cases for the CommunicationSchedule model"""
    
    def test_create_schedule_with_valid_data(self):
        """Test creating a scheduled communication with valid data"""
        donor = DonorFactory()
        template = CommunicationTemplateFactory()
        
        schedule = CommunicationScheduleFactory(
            donor=donor,
            template=template,
            scheduled_date='2024-02-01 09:00:00',
            status='scheduled'
        )
        
        assert schedule.id is not None
        assert schedule.donor == donor
        assert schedule.template == template
        assert schedule.status == 'scheduled'
    
    def test_schedule_str_representation(self):
        """Test the string representation of a schedule"""
        donor = DonorFactory(first_name='Jane', last_name='Smith')
        template = CommunicationTemplateFactory(name='Reminder Email')
        
        schedule = CommunicationScheduleFactory(donor=donor, template=template)
        
        str_repr = str(schedule)
        assert 'Jane Smith' in str_repr or 'Reminder Email' in str_repr
    
    def test_schedule_status_choices(self):
        """Test schedule status choices"""
        donor = DonorFactory()
        template = CommunicationTemplateFactory()
        
        for status in ['scheduled', 'sent', 'cancelled', 'failed']:
            schedule = CommunicationScheduleFactory(
                donor=donor,
                template=template,
                status=status
            )
            assert schedule.status == status
    
    def test_schedule_status_workflow(self):
        """Test schedule status workflow"""
        donor = DonorFactory()
        template = CommunicationTemplateFactory()
        
        schedule = CommunicationScheduleFactory(
            donor=donor,
            template=template,
            status='scheduled'
        )
        
        # Mark as sent
        schedule.status = 'sent'
        schedule.sent_at = '2024-02-01 09:00:00'
        schedule.save()
        
        sent_schedule = CommunicationSchedule.objects.get(id=schedule.id)
        assert sent_schedule.status == 'sent'
        assert sent_schedule.sent_at is not None
    
    def test_schedule_variable_values(self):
        """Test schedule variable values field"""
        donor = DonorFactory()
        template = CommunicationTemplateFactory()
        
        schedule = CommunicationScheduleFactory(
            donor=donor,
            template=template,
            variable_values={'donor_name': 'John', 'amount': '$50'}
        )
        
        assert schedule.variable_values['donor_name'] == 'John'
        assert schedule.variable_values['amount'] == '$50'
    
    def test_schedule_cascade_delete_donor(self):
        """Test that schedules are deleted when donor is deleted"""
        donor = DonorFactory()
        template = CommunicationTemplateFactory()
        schedule = CommunicationScheduleFactory(donor=donor, template=template)
        schedule_id = schedule.id
        
        donor.delete()
        
        with pytest.raises(CommunicationSchedule.DoesNotExist):
            CommunicationSchedule.objects.get(id=schedule_id)
    
    def test_schedule_cascade_delete_template(self):
        """Test that schedules are deleted when template is deleted"""
        donor = DonorFactory()
        template = CommunicationTemplateFactory()
        schedule = CommunicationScheduleFactory(donor=donor, template=template)
        schedule_id = schedule.id
        
        template.delete()
        
        with pytest.raises(CommunicationSchedule.DoesNotExist):
            CommunicationSchedule.objects.get(id=schedule_id)


# =============================================================================
# COMMUNICATION PREFERENCE MODEL TESTS
# =============================================================================

@pytest.mark.django_db
class TestCommunicationPreferenceModel:
    """Test cases for the CommunicationPreference model"""
    
    def test_create_preference_with_valid_data(self):
        """Test creating communication preferences with valid data"""
        donor = DonorFactory()
        preference = CommunicationPreferenceFactory(
            donor=donor,
            email_opt_in=True,
            phone_opt_in=False,
            sms_opt_in=True,
            mail_opt_in=True
        )
        
        assert preference.id is not None
        assert preference.donor == donor
        assert preference.email_opt_in is True
        assert preference.phone_opt_in is False
    
    def test_preference_str_representation(self):
        """Test the string representation of preferences"""
        donor = DonorFactory(first_name='Bob', last_name='Jones')
        preference = CommunicationPreferenceFactory(donor=donor)
        
        str_repr = str(preference)
        assert 'Bob Jones' in str_repr or 'Jones' in str_repr
    
    def test_preference_channel_opt_ins(self):
        """Test all channel opt-in fields"""
        donor = DonorFactory()
        
        preference = CommunicationPreferenceFactory(
            donor=donor,
            email_opt_in=True,
            phone_opt_in=True,
            sms_opt_in=False,
            mail_opt_in=True
        )
        
        assert preference.email_opt_in is True
        assert preference.phone_opt_in is True
        assert preference.sms_opt_in is False
        assert preference.mail_opt_in is True
    
    def test_preference_do_not_contact(self):
        """Test Do Not Contact settings"""
        donor = DonorFactory()
        preference = CommunicationPreferenceFactory(
            donor=donor,
            do_not_contact=True,
            do_not_contact_reason='Requested by donor',
            do_not_contact_until='2024-12-31'
        )
        
        assert preference.do_not_contact is True
        assert preference.do_not_contact_reason == 'Requested by donor'
        assert preference.do_not_contact_until is not None
    
    def test_preference_frequency_choices(self):
        """Test preferred frequency choices"""
        donor = DonorFactory()
        
        for frequency in ['weekly', 'monthly', 'quarterly', 'yearly', 'as_needed']:
            preference = CommunicationPreferenceFactory(
                donor=donor,
                preferred_frequency=frequency
            )
            assert preference.preferred_frequency == frequency
    
    def test_preference_cascade_delete(self):
        """Test that preferences are deleted when donor is deleted"""
        donor = DonorFactory()
        preference = CommunicationPreferenceFactory(donor=donor)
        pref_id = preference.id
        
        donor.delete()
        
        with pytest.raises(CommunicationPreference.DoesNotExist):
            CommunicationPreference.objects.get(id=pref_id)
    
    def test_preference_one_per_donor(self):
        """Test that a donor can only have one preference record"""
        donor = DonorFactory()
        preference1 = CommunicationPreferenceFactory(donor=donor)
        
        # Attempting to create another should fail
        with pytest.raises(Exception):
            CommunicationPreferenceFactory(donor=donor)


# =============================================================================
# CALL LOG MODEL TESTS
# =============================================================================

@pytest.mark.django_db
class TestCallLogModel:
    """Test cases for the CallLog model"""
    
    def test_create_call_log_with_valid_data(self):
        """Test creating a call log with valid data"""
        donor = DonorFactory()
        communication = CommunicationFactory(donor=donor, communication_type='phone')
        
        call_log = CallLogFactory(
            donor=donor,
            communication=communication,
            phone_number='555-1234',
            duration=300,
            outcome='answered'
        )
        
        assert call_log.id is not None
        assert call_log.donor == donor
        assert call_log.communication == communication
        assert call_log.duration == 300
    
    def test_call_log_str_representation(self):
        """Test the string representation of a call log"""
        donor = DonorFactory(first_name='Alice', last_name='Smith')
        call_log = CallLogFactory(donor=donor, phone_number='555-5678')
        
        str_repr = str(call_log)
        assert 'Alice Smith' in str_repr or '555-5678' in str_repr
    
    def test_call_log_direction_choices(self):
        """Test call direction choices"""
        donor = DonorFactory()
        
        for direction in ['inbound', 'outbound']:
            call_log = CallLogFactory(donor=donor, direction=direction)
            assert call_log.direction == direction
    
    def test_call_log_outcome_choices(self):
        """Test call outcome choices"""
        donor = DonorFactory()
        
        for outcome in ['answered', 'voicemail', 'no_answer', 'busy', 'failed']:
            call_log = CallLogFactory(donor=donor, outcome=outcome)
            assert call_log.outcome == outcome
    
    def test_call_log_duration_field(self):
        """Test call duration field"""
        donor = DonorFactory()
        call_log = CallLogFactory(donor=donor, duration=600)
        
        assert call_log.duration == 600
    
    def test_call_log_notes_field(self):
        """Test call log notes field"""
        donor = DonorFactory()
        call_log = CallLogFactory(
            donor=donor,
            notes='Donor expressed interest in monthly giving program'
        )
        
        assert call_log.notes == 'Donor expressed interest in monthly giving program'
    
    def test_call_log_follow_up_fields(self):
        """Test call log follow-up fields"""
        donor = DonorFactory()
        call_log = CallLogFactory(
            donor=donor,
            follow_up_required=True,
            follow_up_date='2024-02-15'
        )
        
        assert call_log.follow_up_required is True
        assert call_log.follow_up_date is not None
    
    def test_call_log_cascade_delete_donor(self):
        """Test that call logs are deleted when donor is deleted"""
        donor = DonorFactory()
        call_log = CallLogFactory(donor=donor)
        log_id = call_log.id
        
        donor.delete()
        
        with pytest.raises(CallLog.DoesNotExist):
            CallLog.objects.get(id=log_id)
    
    def test_call_log_cascade_delete_communication(self):
        """Test that call logs are deleted when communication is deleted"""
        donor = DonorFactory()
        communication = CommunicationFactory(donor=donor)
        call_log = CallLogFactory(donor=donor, communication=communication)
        log_id = call_log.id
        
        communication.delete()
        
        with pytest.raises(CallLog.DoesNotExist):
            CallLog.objects.get(id=log_id)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

@pytest.mark.django_db
class TestCommunicationsIntegration:
    """Integration tests for communication-related functionality"""
    
    def test_donor_communication_history(self):
        """Test a donor's complete communication history"""
        donor = DonorFactory()
        
        # Create various communications
        email = CommunicationFactory(
            donor=donor,
            communication_type='email',
            status='sent',
            subject='Welcome'
        )
        phone = CommunicationFactory(
            donor=donor,
            communication_type='phone',
            status='completed'
        )
        meeting = CommunicationFactory(
            donor=donor,
            communication_type='meeting',
            status='completed'
        )
        
        assert donor.communications.count() == 3
        assert donor.communications.filter(communication_type='email').count() == 1
    
    def test_template_to_schedule_workflow(self):
        """Test workflow from template to scheduled communication"""
        donor = DonorFactory()
        
        # Create template
        template = CommunicationTemplateFactory(
            name='Monthly Newsletter',
            template_type='email',
            subject_template='{{month}} Newsletter',
            body_template='Hello {{donor_name}}',
            variables=['month', 'donor_name']
        )
        
        # Schedule using template
        schedule = CommunicationScheduleFactory(
            donor=donor,
            template=template,
            scheduled_date='2024-03-01 09:00:00',
            variable_values={'month': 'March', 'donor_name': 'John'}
        )
        
        assert schedule.template == template
        assert schedule.variable_values['month'] == 'March'
    
    def test_donor_with_preferences_and_dnc(self):
        """Test donor with communication preferences including DNC"""
        donor = DonorFactory()
        
        # Set preferences
        preferences = CommunicationPreferenceFactory(
            donor=donor,
            email_opt_in=True,
            phone_opt_in=False,
            do_not_contact=False
        )
        
        # Attempt communication
        if not preferences.do_not_contact and preferences.email_opt_in:
            email = CommunicationFactory(donor=donor, communication_type='email')
            assert email.id is not None
        
        assert preferences.email_opt_in is True
        assert preferences.phone_opt_in is False
    
    def test_call_log_linked_to_communication(self):
        """Test call log linked to a phone communication"""
        donor = DonorFactory()
        
        # Create phone communication
        phone_comm = CommunicationFactory(
            donor=donor,
            communication_type='phone',
            direction='outbound',
            status='completed'
        )
        
        # Create associated call log
        call_log = CallLogFactory(
            donor=donor,
            communication=phone_comm,
            duration=450,
            outcome='answered',
            notes='Discussed upcoming event'
        )
        
        assert call_log.communication == phone_comm
        assert call_log.duration == 450
    
    def test_follow_up_communications(self):
        """Test tracking follow-up communications"""
        donor = DonorFactory()
        
        # Initial communication requiring follow-up
        initial = CommunicationFactory(
            donor=donor,
            communication_type='phone',
            requires_follow_up=True,
            follow_up_date='2024-02-01'
        )
        
        # Follow-up communication
        follow_up = CommunicationFactory(
            donor=donor,
            communication_type='email',
            status='sent'
        )
        
        assert donor.communications.filter(requires_follow_up=True).count() == 1
        assert donor.communications.filter(communication_type='email').count() == 1
