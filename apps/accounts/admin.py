from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ['email', 'role', 'region', 'is_verified', 'is_active', 'date_joined']
    list_filter = ['role', 'region', 'is_verified', 'is_active']
    search_fields = ['email', 'phone_number']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('phone_number', 'avatar')}),
        ('Status', {'fields': ('role', 'region', 'is_verified', 'is_active', 'is_staff', 'is_superuser')}),
        ('Dates', {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2', 'role')}),
    )
    readonly_fields = ['date_joined', 'last_login']
