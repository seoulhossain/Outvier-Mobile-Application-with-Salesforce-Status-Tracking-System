"""
Management command to seed demo data for local development / capstone demo.
Run: .venv/bin/python manage.py seed_demo
Creates student user 'alex', 2 demo applications with full history/docs/notifications.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

from applications.models import Application, ApplicationStatusHistory, Document, OfferDetail, CommunicationLog
from notifications.models import Notification
from sync_logs.models import SyncLog

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed demo data for development and presentation'

    def handle(self, *args, **options):
        self.stdout.write('Seeding demo data…')

        # ── Student user ──────────────────────────────────────────────────────
        student, created = User.objects.get_or_create(
            username='alex',
            defaults={
                'email': 'alex@student.edu.au',
                'first_name': 'Alex',
                'last_name': 'Johnson',
                'role': 'student',
                'student_id': 'S20240001',
            }
        )
        if created:
            student.set_password('alex1234')
            student.save()
            self.stdout.write(self.style.SUCCESS('  Created student: alex / alex1234'))
        else:
            self.stdout.write('  Student alex already exists')

        # ── Application 1: Conditional Offer ─────────────────────────────────
        app1, _ = Application.objects.get_or_create(
            salesforce_id='APP-2024-000123',
            defaults={
                'student': student,
                'status': Application.CONDITIONAL_OFFER,
                'program': 'MSc Computer Science',
                'intake_period': 'Semester 1, 2024',
            }
        )

        # Status history for app1
        now = timezone.now()
        history_data = [
            (Application.SUBMITTED, now - timedelta(days=10), 'Application received'),
            (Application.UNDER_REVIEW, now - timedelta(days=9), 'Assigned to admissions officer'),
            (Application.CONDITIONAL_OFFER, now - timedelta(days=2), 'Conditional offer issued'),
        ]
        for status, ts, notes in history_data:
            ApplicationStatusHistory.objects.get_or_create(
                application=app1, status=status,
                defaults={'notes': notes, 'changed_at': ts}
            )

        # Documents for app1 (matching wireframe)
        docs1 = [
            ('Passport', 'verified'),
            ('Academic Transcript', 'verified'),
            ('Proof of English Proficiency', 'pending'),
            ('Statement of Purpose', 'verified'),
            ('Letter of Recommendation', 'missing'),
            ('CV / Resume', 'verified'),
        ]
        for doc_type, vstatus in docs1:
            Document.objects.get_or_create(
                application=app1, doc_type=doc_type,
                defaults={'verification_status': vstatus}
            )

        # Offer detail for app1
        OfferDetail.objects.get_or_create(
            application=app1,
            defaults={
                'offer_type': 'conditional',
                'deadline': now + timedelta(days=30),
                'remarks': 'Minimum GPA 3.5; Proof of English Proficiency; Submit Letters of Recommendation. '
                           'Current Stage: Offer Issuance. Next Steps: Review offer, meet conditions.',
            }
        )

        # ── Application 2: Under Review ───────────────────────────────────────
        app2, _ = Application.objects.get_or_create(
            salesforce_id='APP-2024-000456',
            defaults={
                'student': student,
                'status': Application.UNDER_REVIEW,
                'program': 'MBA',
                'intake_period': 'Semester 2, 2024',
            }
        )
        ApplicationStatusHistory.objects.get_or_create(
            application=app2, status=Application.SUBMITTED,
            defaults={'notes': 'Application received', 'changed_at': now - timedelta(days=4)}
        )
        ApplicationStatusHistory.objects.get_or_create(
            application=app2, status=Application.UNDER_REVIEW,
            defaults={'notes': 'Under review by admissions', 'changed_at': now - timedelta(days=2)}
        )
        docs2 = [
            ('Passport', 'verified'),
            ('Academic Transcript', 'pending'),
            ('Work Experience Letter', 'missing'),
        ]
        for doc_type, vstatus in docs2:
            Document.objects.get_or_create(
                application=app2, doc_type=doc_type,
                defaults={'verification_status': vstatus}
            )

        # ── Communication logs ────────────────────────────────────────────────
        comm_data = [
            (app1, 'TASK-SF-001', 'call', 'Initial Enquiry Call',
             'Spoke with Alex regarding program requirements and next steps.'),
            (app1, 'TASK-SF-002', 'email', 'Conditional Offer Issued',
             'Sent formal conditional offer letter. Awaiting acceptance.'),
            (app1, 'TASK-SF-003', 'note', 'Missing Document Follow-up',
             'Student needs to submit Letter of Recommendation by end of month.'),
            (app2, 'TASK-SF-004', 'call', 'Application Review Call',
             'Discussed MBA program structure. Application under review.'),
        ]
        for app, sf_id, log_type, subject, description in comm_data:
            CommunicationLog.objects.get_or_create(
                salesforce_task_id=sf_id,
                defaults={
                    'application': app,
                    'log_type': log_type,
                    'subject': subject,
                    'description': description,
                }
            )

        # ── Notifications ─────────────────────────────────────────────────────
        notif_data = [
            (student, 'Application Status Changed: Your application has been moved to \'Conditional Offer\' stage.', 'email', False),
            (student, 'New Document Verified: Your Statement of Purpose has been successfully verified.', 'email', True),
            (student, 'Deadline Approaching: The deadline to accept your conditional offer is 30 June 2024.', 'push', False),
            (student, 'English Proficiency Pending: Please ensure your Proof of English Proficiency is uploaded.', 'push', True),
        ]
        for i, (user, message, channel, is_read) in enumerate(notif_data):
            Notification.objects.get_or_create(
                student=user, message=message,
                defaults={
                    'channel': channel,
                    'is_read': is_read,
                }
            )

        # ── Sync Logs ─────────────────────────────────────────────────────────
        sync_data = [
            ('success', 3, '', now - timedelta(minutes=5)),
            ('success', 1, '', now - timedelta(minutes=20)),
            ('failed', 0, 'Salesforce OAuth token expired. Retrying…', now - timedelta(minutes=35)),
            ('success', 5, '', now - timedelta(hours=1)),
        ]
        for sstatus, records, error, ts in sync_data:
            SyncLog.objects.get_or_create(
                sync_time=ts,
                defaults={'status': sstatus, 'records_updated': records, 'error_message': error}
            )

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully!'))
        self.stdout.write('  Student login: alex / alex1234')
        self.stdout.write('  Admin login:   admin / arka')
