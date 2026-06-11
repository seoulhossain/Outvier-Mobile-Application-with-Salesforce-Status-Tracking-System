from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'student_id', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Outvier Fields', {'fields': ('role', 'student_id', 'phone_number', 'push_token')}),
    )
    search_fields = ['username', 'email', 'student_id']
