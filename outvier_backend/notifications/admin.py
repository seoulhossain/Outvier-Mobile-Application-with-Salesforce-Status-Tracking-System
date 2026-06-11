from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['student', 'channel', 'is_read', 'sent_at']
    list_filter = ['channel', 'is_read']
    readonly_fields = ['student', 'message', 'channel', 'sent_at']
    search_fields = ['student__username', 'student__email']
