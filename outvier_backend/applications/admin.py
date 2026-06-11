from django.contrib import admin
from .models import Application, ApplicationStatusHistory, Document, OfferDetail


class ApplicationStatusHistoryInline(admin.TabularInline):
    model = ApplicationStatusHistory
    extra = 0
    readonly_fields = ['status', 'changed_at', 'notes']


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['student', 'salesforce_id', 'status', 'program', 'intake_period', 'updated_at']
    list_filter = ['status', 'intake_period']
    search_fields = ['student__username', 'salesforce_id', 'program']
    inlines = [ApplicationStatusHistoryInline, DocumentInline]
    readonly_fields = ['salesforce_id', 'created_at', 'updated_at']


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    list_display = ['application', 'offer_type', 'deadline']
    list_filter = ['offer_type']
