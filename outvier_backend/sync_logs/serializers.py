from rest_framework import serializers
from .models import SyncLog


class SyncLogSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = SyncLog
        fields = [
            'id', 'sync_time', 'status', 'status_display',
            'records_updated', 'error_message', 'created_at',
        ]
