import logging
from celery import shared_task
from django.utils import timezone

from .client import (
    get_salesforce_client,
    fetch_applications,
    fetch_documents,
    fetch_offer_details,
    fetch_communication_logs,
)
from .mapper import map_application_record
from sync_logs.models import SyncLog

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_salesforce_data(self):
    """
    FR-09, FR-10, NFR-02: Periodic Celery task — polls Salesforce, updates
    PostgreSQL, logs every cycle. Scheduled every 15 minutes max.
    On failure, retries up to 3 times before logging as failed (FR-12).
    """
    sync_log = SyncLog.objects.create(
        status=SyncLog.IN_PROGRESS,
        sync_time=timezone.now(),
    )
    records_updated = 0

    try:
        sf_client = get_salesforce_client()
        sf_records = fetch_applications(sf_client)

        for sf_record in sf_records:
            sf_id = sf_record.get('Id', '')
            try:
                docs = fetch_documents(sf_client, sf_id)
                offer = fetch_offer_details(sf_client, sf_id)
                comm_logs = fetch_communication_logs(sf_client, sf_id)
                application, status_changed = map_application_record(
                    sf_record, docs, offer, comm_logs
                )

                if application and status_changed:
                    records_updated += 1
                    # Trigger notification asynchronously (FR-08)
                    from notifications.engine import trigger_status_change_notification
                    trigger_status_change_notification.delay(application.id)

            except Exception as record_exc:
                logger.error(
                    "Error processing Salesforce record %s: %s", sf_id, record_exc
                )
                # Continue with next record — do not crash entire sync (FR-12)

        sync_log.status = SyncLog.SUCCESS
        sync_log.records_updated = records_updated
        sync_log.save()
        logger.info("Salesforce sync complete. %d records updated.", records_updated)

    except Exception as exc:
        sync_log.status = SyncLog.FAILED
        sync_log.error_message = str(exc)
        sync_log.save()
        logger.error("Salesforce sync failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def sync_single_record(self, salesforce_id):
    """
    Targeted sync for a single Salesforce record, triggered by incoming webhook.
    Spec requirement: webhook processing.
    """
    try:
        sf_client = get_salesforce_client()

        # Fetch just this record via SOQL with Id filter
        query = (
            "SELECT Id, Name, Email__c, Status__c, Program__c, "
            "Intake_Period__c, LastModifiedDate "
            f"FROM Opportunity WHERE Id = '{salesforce_id}' LIMIT 1"
        )
        result = sf_client.query(query)
        records = result.get('records', [])

        if not records:
            logger.warning("sync_single_record: Salesforce record %s not found.", salesforce_id)
            return

        sf_record = records[0]
        docs = fetch_documents(sf_client, salesforce_id)
        offer = fetch_offer_details(sf_client, salesforce_id)
        comm_logs = fetch_communication_logs(sf_client, salesforce_id)
        application, status_changed = map_application_record(sf_record, docs, offer, comm_logs)

        if application and status_changed:
            from notifications.engine import trigger_status_change_notification
            trigger_status_change_notification.delay(application.id)
            logger.info("Webhook sync complete for %s — status changed.", salesforce_id)
        else:
            logger.info("Webhook sync complete for %s — no status change.", salesforce_id)

    except Exception as exc:
        logger.error("sync_single_record failed for %s: %s", salesforce_id, exc)
        raise self.retry(exc=exc)
