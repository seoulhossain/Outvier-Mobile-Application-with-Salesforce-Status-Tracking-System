from django.db import models


class SyncLog(models.Model):
    """
    Records every Salesforce synchronisation cycle.
    FR-10: date, time, status, success/failure of every Salesforce data access.
    UC-04: Administrators view this table via the monitoring dashboard.
    """
    SUCCESS = 'success'
    FAILED = 'failed'
    IN_PROGRESS = 'in_progress'

    STATUS_CHOICES = [
        (SUCCESS, 'Success'),
        (FAILED, 'Failed'),
        (IN_PROGRESS, 'In Progress'),
    ]

    sync_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    records_updated = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sync_logs'
        ordering = ['-sync_time']

    def __str__(self):
        return f"{self.sync_time} — {self.status} ({self.records_updated} updated)"
