import logging
from accounts.models import User
from applications.models import Application, ApplicationStatusHistory, Document, OfferDetail, CommunicationLog

logger = logging.getLogger(__name__)

# FR-02: Salesforce status string → internal status constant
STATUS_MAP = {
    'Submitted': Application.SUBMITTED,
    'Under Review': Application.UNDER_REVIEW,
    'Conditional Offer': Application.CONDITIONAL_OFFER,
    'Document Missing': Application.DOCUMENT_MISSING,
    'Unconditional Offer': Application.UNCONDITIONAL_OFFER,
    'Enrolled': Application.ENROLLED,
    'Rejected': Application.REJECTED,
}

DOCUMENT_STATUS_MAP = {
    'Verified': Document.VERIFIED,
    'Pending': Document.PENDING,
    'Missing': Document.MISSING,
}


def map_application_record(sf_record, documents=None, offer=None, communication_logs=None):
    """
    Map a Salesforce Opportunity record to the internal Application model.
    FR-02. Creates or updates the application and records a status history entry.
    Returns (application, status_changed: bool).
    """
    salesforce_id = sf_record.get('Id', '')
    email = sf_record.get('Email__c', '')
    sf_status = sf_record.get('Status__c', 'Submitted')
    internal_status = STATUS_MAP.get(sf_status, Application.SUBMITTED)

    try:
        student = User.objects.get(email=email)
    except User.DoesNotExist:
        logger.warning("No local user found for Salesforce email '%s'. Skipping record.", email)
        return None, False

    application, created = Application.objects.get_or_create(
        salesforce_id=salesforce_id,
        defaults={
            'student': student,
            'status': internal_status,
            'program': sf_record.get('Program__c', ''),
            'intake_period': sf_record.get('Intake_Period__c', ''),
        },
    )

    status_changed = False

    if not created and application.status != internal_status:
        application.status = internal_status
        application.program = sf_record.get('Program__c', application.program)
        application.intake_period = sf_record.get('Intake_Period__c', application.intake_period)
        application.save()
        status_changed = True
        # Record transition in audit trail (FR-04)
        ApplicationStatusHistory.objects.create(
            application=application,
            status=internal_status,
        )

    if documents:
        _sync_documents(application, documents)

    if offer:
        _sync_offer(application, offer)

    if communication_logs:
        _sync_communication_logs(application, communication_logs)

    return application, status_changed


def _sync_documents(application, sf_documents):
    """
    Sync document verification records. Uses unique_together constraint to
    prevent duplicates (NFR-06). FR-05.
    """
    for sf_doc in sf_documents:
        doc_type = sf_doc.get('Document_Type__c', '')
        v_status = DOCUMENT_STATUS_MAP.get(
            sf_doc.get('Verification_Status__c', 'Pending'),
            Document.PENDING,
        )
        Document.objects.update_or_create(
            application=application,
            doc_type=doc_type,
            defaults={
                'verification_status': v_status,
                'uploaded_at': sf_doc.get('Uploaded_At__c'),
            },
        )


def _sync_offer(application, sf_offer):
    """
    Sync offer details from Salesforce. FR-06.
    """
    offer_type_raw = sf_offer.get('Offer_Type__c', '')
    offer_type = (
        OfferDetail.UNCONDITIONAL
        if 'Unconditional' in offer_type_raw
        else OfferDetail.CONDITIONAL
    )
    OfferDetail.objects.update_or_create(
        application=application,
        defaults={
            'offer_type': offer_type,
            'deadline': sf_offer.get('Deadline__c'),
            'remarks': sf_offer.get('Remarks__c', ''),
        },
    )


def _sync_communication_logs(application, sf_tasks):
    """
    Sync Salesforce Task records as CommunicationLog entries.
    Uses salesforce_task_id unique constraint to prevent duplicates.
    Spec requirement: Communication history logs.
    """
    TYPE_MAP = {
        'Call': CommunicationLog.CALL,
        'Email': CommunicationLog.EMAIL,
        'Note': CommunicationLog.NOTE,
    }
    for task in sf_tasks:
        task_id = task.get('Id', '')
        if not task_id:
            continue
        log_type = TYPE_MAP.get(task.get('Type', ''), CommunicationLog.OTHER)
        CommunicationLog.objects.update_or_create(
            salesforce_task_id=task_id,
            defaults={
                'application': application,
                'log_type': log_type,
                'subject': task.get('Subject', ''),
                'description': task.get('Description', ''),
                'activity_date': task.get('ActivityDate'),
            },
        )
