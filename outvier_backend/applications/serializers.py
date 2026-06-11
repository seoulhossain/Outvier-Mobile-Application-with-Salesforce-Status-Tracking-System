from rest_framework import serializers
from .models import Application, ApplicationStatusHistory, Document, OfferDetail, CommunicationLog


class DocumentSerializer(serializers.ModelSerializer):
    verification_status_display = serializers.CharField(
        source='get_verification_status_display', read_only=True
    )

    class Meta:
        model = Document
        fields = ['id', 'doc_type', 'verification_status', 'verification_status_display', 'uploaded_at', 'notes']


class OfferDetailSerializer(serializers.ModelSerializer):
    offer_type_display = serializers.CharField(source='get_offer_type_display', read_only=True)

    class Meta:
        model = OfferDetail
        fields = ['offer_type', 'offer_type_display', 'deadline', 'remarks']


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ApplicationStatusHistory
        fields = ['status', 'status_display', 'changed_at', 'notes']


class CommunicationLogSerializer(serializers.ModelSerializer):
    log_type_display = serializers.CharField(source='get_log_type_display', read_only=True)

    class Meta:
        model = CommunicationLog
        fields = ['id', 'log_type', 'log_type_display', 'subject', 'description', 'activity_date', 'created_at']


class ApplicationSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)
    offer_detail = OfferDetailSerializer(read_only=True)
    status_history = ApplicationStatusHistorySerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    communication_logs = CommunicationLogSerializer(many=True, read_only=True)
    student_username = serializers.CharField(source='student.username', read_only=True)
    student_name = serializers.SerializerMethodField()

    def get_student_name(self, obj):
        full = f"{obj.student.first_name} {obj.student.last_name}".strip()
        return full if full else obj.student.username

    class Meta:
        model = Application
        fields = [
            'id', 'salesforce_id', 'status', 'status_display',
            'program', 'intake_period', 'created_at', 'updated_at',
            'student_username', 'student_name',
            'documents', 'offer_detail', 'status_history', 'communication_logs',
        ]
