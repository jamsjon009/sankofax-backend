from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.utils.html import format_html
from django.urls import reverse
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm
from .models import User, AdminUserProxy, CompanyUserProxy, RegularUserProxy

ADMIN_ROLES = [User.Role.STAFF, User.Role.MODERATOR, User.Role.ADMIN, User.Role.SUPER_ADMIN]


# ── Admin Users (Staff / Moderator / Admin / Super Admin) ─────────────────────

@admin.register(AdminUserProxy)
class AdminUserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ['email', 'display_role', 'is_staff', 'is_superuser', 'is_active', 'date_joined', 'actions_column']
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['email', 'phone_number']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('email', 'password_change_link')}),
        ('Personal', {'fields': ('phone_number', 'avatar')}),
        ('Role & Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Dates', {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_staff', 'is_superuser'),
        }),
    )
    readonly_fields = ['date_joined', 'last_login', 'password_change_link']

    def password_change_link(self, obj):
        if obj and obj.pk:
            url = f'/admin/accounts/adminuserproxy/{obj.pk}/password/'
            return format_html(
                '<a href="{}" style="display:inline-flex;align-items:center;gap:4px;color:#6366f1;">'
                '<span class="material-symbols-outlined" style="font-size:16px;">key</span> Change Password</a>',
                url
            )
        return '-'
    password_change_link.short_description = 'Password'

    @admin.display(description='Role')
    def display_role(self, obj):
        return obj.get_role_display()

    @admin.display(description='Actions')
    def actions_column(self, obj):
        edit_url = reverse('admin:accounts_adminuserproxy_change', args=[obj.pk])
        delete_url = reverse('admin:accounts_adminuserproxy_delete', args=[obj.pk])
        return format_html(
            '<a href="{}" title="Edit" style="margin-right:12px;color:#6366f1;display:inline-flex;align-items:center;">'
            '<span class="material-symbols-outlined" style="font-size:18px;">edit</span></a>'
            '<a href="{}" title="Delete" style="color:#ef4444;display:inline-flex;align-items:center;" '
            'onclick="return confirm(\'Are you sure you want to delete this admin?\')">'
            '<span class="material-symbols-outlined" style="font-size:18px;">delete</span></a>',
            edit_url, delete_url
        )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(role__in=ADMIN_ROLES)

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# ── Company Users (Business Owners) ───────────────────────────────────────────

@admin.register(CompanyUserProxy)
class CompanyUserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ['email', 'region', 'is_verified', 'is_active', 'date_joined']
    list_filter = ['region', 'is_verified', 'is_active']
    search_fields = ['email', 'phone_number']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('phone_number', 'avatar')}),
        ('Status', {'fields': ('region', 'is_verified', 'is_active')}),
        ('Dates', {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'region'),
        }),
    )
    readonly_fields = ['date_joined', 'last_login']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(role=User.Role.BUSINESS_OWNER)

    def save_model(self, request, obj, form, change):
        obj.role = User.Role.BUSINESS_OWNER
        super().save_model(request, obj, form, change)


# ── Regular Users (Visitors) ──────────────────────────────────────────────────

@admin.register(RegularUserProxy)
class RegularUserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ['email', 'region', 'is_verified', 'is_active', 'date_joined']
    list_filter = ['region', 'is_verified', 'is_active']
    search_fields = ['email', 'phone_number']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('phone_number', 'avatar')}),
        ('Status', {'fields': ('region', 'is_verified', 'is_active')}),
        ('Dates', {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    readonly_fields = ['date_joined', 'last_login']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(role=User.Role.VISITOR)


# ── Hide base User model from admin (use proxy models above) ──────────────────
# User is not registered directly — all management goes through proxy models.
