from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    Records every alert dispatched to a student.
    Stores channel, timestamp and message content. FR-08.
    """
    EMAIL = 'email'
    PUSH = 'push'

    CHANNEL_CHOICES = [
        (EMAIL, 'Email'),
        (PUSH, 'Push'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    message = models.TextField()
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default=EMAIL)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'notifications'
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.student.username} | {self.channel} | {self.sent_at}"
