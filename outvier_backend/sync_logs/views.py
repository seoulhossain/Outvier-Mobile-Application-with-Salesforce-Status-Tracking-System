from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import SyncLog
from .serializers import SyncLogSerializer


class IsAdministrator(IsAuthenticated):
    """FR-07: Sync logs are restricted to administrator role only."""

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_admin()


class SyncLogListView(APIView):
    """
    FR-10, UC-04: Returns all sync log entries to authenticated administrators.
    Students cannot access this endpoint.
    """
    permission_classes = [IsAdministrator]

    def get(self, request):
        logs = SyncLog.objects.all()
        serializer = SyncLogSerializer(logs, many=True)
        return Response(serializer.data)
