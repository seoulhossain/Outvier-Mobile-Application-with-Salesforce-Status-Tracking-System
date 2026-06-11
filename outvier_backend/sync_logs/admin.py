from django.contrib import admin
from .models import SyncLog


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ['sync_time', 'status', 'records_updated', 'created_at']
    list_filter = ['status']
    readonly_fields = ['sync_time', 'status', 'records_updated', 'error_message', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
