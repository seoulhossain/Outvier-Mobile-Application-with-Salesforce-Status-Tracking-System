import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class SalesforceWebhookView(View):
    """
    Receives Salesforce outbound messages (JSON format).
    Verifies HMAC-SHA256 signature before processing to ensure the
    request genuinely originates from Salesforce (security requirement).
    Triggers a targeted single-record sync via Celery.
    Spec requirement: webhook processing.
    """

    def post(self, request):
        raw_body = request.body

        # --- Signature verification (prevents forged webhook calls) ---
        webhook_secret = getattr(settings, 'SALESFORCE_WEBHOOK_SECRET', '')
        if webhook_secret:
            signature = request.META.get('HTTP_X_SALESFORCE_SIGNATURE', '')
            expected = hmac.new(
                webhook_secret.encode('utf-8'),
                raw_body,
                hashlib.sha256,
            ).hexdigest()
            if not hmac.compare_digest(signature, expected):
                logger.warning(
                    "Salesforce webhook: rejected request with invalid signature from %s.",
                    request.META.get('REMOTE_ADDR', 'unknown'),
                )
                return HttpResponse(status=403)

        # --- Parse payload ---
        try:
            payload = json.loads(raw_body)
        except (json.JSONDecodeError, ValueError) as exc:
            logger.error("Salesforce webhook: malformed JSON payload — %s", exc)
            return HttpResponse(status=400)

        # Salesforce outbound messages may send a single record or a list
        records = payload if isinstance(payload, list) else [payload]

        queued = 0
        for record in records:
            sf_id = record.get('Id') or record.get('salesforce_id') or record.get('id')
            if not sf_id:
                logger.warning("Salesforce webhook: record missing Id field, skipping.")
                continue
            from salesforce_sync.tasks import sync_single_record
            sync_single_record.delay(sf_id)
            queued += 1

        logger.info("Salesforce webhook: queued %d record(s) for sync.", queued)
        return HttpResponse(status=200)
