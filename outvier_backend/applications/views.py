from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Application, CommunicationLog
from .serializers import ApplicationSerializer, CommunicationLogSerializer


class StudentApplicationListView(APIView):
    """
    FR-03, FR-04, FR-07: Students see only their own applications.
    Administrators see all applications.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_admin():
            applications = Application.objects.select_related('student').prefetch_related(
                'documents', 'status_history', 'offer_detail', 'communication_logs'
            ).all()
        else:
            applications = Application.objects.filter(
                student=request.user
            ).prefetch_related('documents', 'status_history', 'offer_detail', 'communication_logs')

        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)


class StudentApplicationDetailView(APIView):
    """
    FR-04, FR-05, FR-06: Full detail — status, documents, offer, communication logs.
    Students can only access their own record (RBAC, FR-07).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            if request.user.is_admin():
                application = Application.objects.prefetch_related(
                    'documents', 'status_history', 'offer_detail', 'communication_logs'
                ).get(pk=pk)
            else:
                application = Application.objects.prefetch_related(
                    'documents', 'status_history', 'offer_detail', 'communication_logs'
                ).get(pk=pk, student=request.user)
        except Application.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ApplicationSerializer(application)
        return Response(serializer.data)


class CommunicationLogListView(APIView):
    """
    Returns communication history logs for a given application.
    Students can only access logs for their own applications (RBAC).
    Spec requirement: Communication history logs.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            if request.user.is_admin():
                application = Application.objects.get(pk=pk)
            else:
                application = Application.objects.get(pk=pk, student=request.user)
        except Application.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        logs = CommunicationLog.objects.filter(application=application)
        serializer = CommunicationLogSerializer(logs, many=True)
        return Response(serializer.data)
