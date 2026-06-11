from django.urls import path
from .views import StudentApplicationListView, StudentApplicationDetailView, CommunicationLogListView

urlpatterns = [
    path('applications/', StudentApplicationListView.as_view(), name='application_list'),
    path('applications/<int:pk>/', StudentApplicationDetailView.as_view(), name='application_detail'),
    path('applications/<int:pk>/communication-logs/', CommunicationLogListView.as_view(), name='communication_logs'),
]
