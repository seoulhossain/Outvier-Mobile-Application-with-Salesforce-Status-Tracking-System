from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'message', 'channel', 'channel_display', 'sent_at', 'is_read']
