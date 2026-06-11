import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'outvier_backend.settings')

app = Celery('outvier_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# FR-09, NFR-02: Poll Salesforce every 15 minutes max
app.conf.beat_schedule = {
    'sync-salesforce-every-15-minutes': {
        'task': 'salesforce_sync.tasks.sync_salesforce_data',
        'schedule': crontab(minute='*/15'),
    },
}
