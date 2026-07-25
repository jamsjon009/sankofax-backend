from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import UserProfile, CompanyProfile, IdentityBadge


@admin.register(IdentityBadge)
class IdentityBadgeAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'color', 'order']
    list_editable = ['order']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ['user', 'country', 'city']
    list_per_page = 10
    search_fields = ['user__email', 'city', 'country']


@admin.register(CompanyProfile)
class CompanyProfileAdmin(ModelAdmin):
    list_display = ['company_name', 'owner', 'is_verified', 'company_size', 'created_at']
    list_per_page = 10
    list_filter = ['is_verified', 'company_size', 'badges']
    search_fields = ['company_name', 'owner__email']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    filter_horizontal = ['badges']
    actions = ['verify_companies']

    @admin.action(description='Mark selected companies as verified')
    def verify_companies(self, request, queryset):
        queryset.update(is_verified=True)
