from django.urls import path
from .views import SyncLogListView

urlpatterns = [
    path('sync-logs/', SyncLogListView.as_view(), name='sync_logs'),
]
