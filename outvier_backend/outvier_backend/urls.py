from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from salesforce_sync.webhook import SalesforceWebhookView


def api_root(request):
    return JsonResponse({
        "project": "Outvier Salesforce Status Tracking System",
        "version": "1.0",
        "endpoints": {
            "admin": "/admin/",
            "login": "/api/auth/login/",
            "refresh": "/api/auth/refresh/",
            "register": "/api/auth/register/",
            "profile": "/api/auth/profile/",
            "applications": "/api/applications/",
            "communication_logs": "/api/applications/<id>/communication-logs/",
            "notifications": "/api/notifications/",
            "sync_logs": "/api/admin/sync-logs/",
            "webhook_salesforce": "/api/webhooks/salesforce/",
        }
    })


urlpatterns = [
    path('', api_root, name='api_root'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('applications.urls')),
    path('api/', include('notifications.urls')),
    path('api/admin/', include('sync_logs.urls')),
    path('api/webhooks/salesforce/', SalesforceWebhookView.as_view(), name='salesforce_webhook'),
]
