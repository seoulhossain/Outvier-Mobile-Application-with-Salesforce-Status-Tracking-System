import hashlib
import hmac
import json
import logging

import requests
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task
def trigger_status_change_notification(application_id):
    """
    FR-08: Triggered by sync task when a Salesforce record status changes.
    Sends email notification and records a push notification entry.
    Does not crash the sync if notification delivery fails (FR-12).
    """
    from applications.models import Application
    from .models import Notification

    try:
        application = Application.objects.select_related('student').get(pk=application_id)
    except Application.DoesNotExist:
        logger.error("Notification skipped — application %s not found.", application_id)
        return

    student = application.student
    status_display = application.get_status_display()

    message = (
        f"Dear {student.first_name or student.username},\n\n"
        f"Your application status has been updated to: {status_display}.\n\n"
        f"Program: {application.program}\n"
        f"Intake: {application.intake_period}\n\n"
        "Log in to the Outvier app to see full details.\n\n"
        "Outvier Team"
    )

    # Email channel
    if student.email:
        try:
            send_mail(
                subject=f"Application Status Update: {status_display}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                fail_silently=False,
            )
            Notification.objects.create(
                student=student,
                message=message,
                channel=Notification.EMAIL,
            )
            logger.info("Email sent to %s for application %s.", student.email, application_id)
        except Exception as exc:
            logger.error("Email delivery failed for %s: %s", student.email, exc)

    # Push channel
    _dispatch_push(student, status_display, application)


def _dispatch_push(student, status_display, application):
    """
    Push notification dispatch via Firebase Cloud Messaging (FCM) HTTP v1 API.
    Stores a Notification record regardless of FCM delivery result (FR-08).
    Requires FCM_SERVER_KEY in settings and a push_token on the user profile.
    """
    from .models import Notification

    push_token = getattr(student, 'push_token', None)
    if not push_token:
        return

    message_body = f"Your application status is now: {status_display}"
    Notification.objects.create(
        student=student,
        message=message_body,
        channel=Notification.PUSH,
    )

    fcm_key = getattr(settings, 'FCM_SERVER_KEY', '')
    if not fcm_key:
        logger.warning(
            "FCM_SERVER_KEY not configured. Push notification recorded but not delivered for %s.",
            student.username,
        )
        return

    payload = {
        "to": push_token,
        "notification": {
            "title": "Outvier — Status Update",
            "body": message_body,
            "sound": "default",
        },
        "data": {
            "application_id": str(application.id),
            "status": application.status,
        },
    }

    try:
        response = requests.post(
            "https://fcm.googleapis.com/fcm/send",
            json=payload,
            headers={
                "Authorization": f"key={fcm_key}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()
        if result.get('failure', 0) > 0:
            logger.warning(
                "FCM delivery failed for %s: %s",
                student.username,
                result.get('results'),
            )
        else:
            logger.info("FCM push sent to %s.", student.username)
    except requests.RequestException as exc:
        logger.error("FCM HTTP request failed for %s: %s", student.username, exc)
