from django.db import models
from django.conf import settings


class Application(models.Model):
    """
    Central entity capturing each student application instance and current state.
    FR-02, FR-04. Maps to Salesforce Opportunity/Lead/Custom Object records.
    """
    # Status values exactly as defined in state diagram (Design doc §3.6)
    SUBMITTED = 'submitted'
    UNDER_REVIEW = 'under_review'
    CONDITIONAL_OFFER = 'conditional_offer'
    DOCUMENT_MISSING = 'document_missing'
    UNCONDITIONAL_OFFER = 'unconditional_offer'
    ENROLLED = 'enrolled'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (SUBMITTED, 'Submitted'),
        (UNDER_REVIEW, 'Under Review'),
        (CONDITIONAL_OFFER, 'Conditional Offer'),
        (DOCUMENT_MISSING, 'Document Missing'),
        (UNCONDITIONAL_OFFER, 'Unconditional Offer'),
        (ENROLLED, 'Enrolled'),
        (REJECTED, 'Rejected'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
    )
    # Unique constraint on salesforce_id prevents duplicate records on sync (NFR-06)
    salesforce_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=SUBMITTED)
    program = models.CharField(max_length=200, blank=True)
    intake_period = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'applications'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.student.username} | {self.program} | {self.status}"


class ApplicationStatusHistory(models.Model):
    """
    Audit trail of all status transitions. FR-04, FR-08.
    Directly mirrors the state diagram from Design doc §3.6.
    """
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='status_history',
    )
    status = models.CharField(max_length=30, choices=Application.STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'application_status_history'
        ordering = ['-changed_at']


class Document(models.Model):
    """
    Per-document verification status for each application. FR-05.
    """
    VERIFIED = 'verified'
    PENDING = 'pending'
    MISSING = 'missing'

    VERIFICATION_CHOICES = [
        (VERIFIED, 'Verified'),
        (PENDING, 'Pending'),
        (MISSING, 'Missing'),
    ]

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='documents',
    )
    doc_type = models.CharField(max_length=100)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_CHOICES,
        default=PENDING,
    )
    uploaded_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'documents'
        unique_together = [('application', 'doc_type')]


class CommunicationLog(models.Model):
    """
    Salesforce Activity/Task communication history logs synced per application.
    Covers calls, emails, and notes logged by admission officers.
    Explicitly required by project spec (Communication history logs).
    """
    CALL = 'call'
    EMAIL = 'email'
    NOTE = 'note'
    OTHER = 'other'

    LOG_TYPE_CHOICES = [
        (CALL, 'Call'),
        (EMAIL, 'Email'),
        (NOTE, 'Note'),
        (OTHER, 'Other'),
    ]

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='communication_logs',
    )
    salesforce_task_id = models.CharField(max_length=100, unique=True)
    log_type = models.CharField(max_length=10, choices=LOG_TYPE_CHOICES, default=OTHER)
    subject = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    activity_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'communication_logs'
        ordering = ['-activity_date', '-created_at']

    def __str__(self):
        return f"{self.log_type} | {self.subject} | {self.application}"


class OfferDetail(models.Model):
    """
    Conditional / unconditional offer data, deadlines and admission officer remarks.
    FR-06.
    """
    CONDITIONAL = 'conditional'
    UNCONDITIONAL = 'unconditional'

    OFFER_TYPE_CHOICES = [
        (CONDITIONAL, 'Conditional'),
        (UNCONDITIONAL, 'Unconditional'),
    ]

    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name='offer_detail',
    )
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)
    deadline = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'offer_details'
