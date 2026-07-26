from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import UserProfile, CompanyProfile, IdentityBadge, VerificationRequest


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
    list_display = ['company_name', 'owner', 'verification_level', 'is_verified', 'company_size', 'created_at']
    list_per_page = 10
    list_filter = ['verification_level', 'is_verified', 'company_size', 'badges']
    search_fields = ['company_name', 'owner__email']
    readonly_fields = ['slug', 'verified_at', 'verification_expires_at', 'created_at', 'updated_at']
    filter_horizontal = ['badges']
    actions = ['grant_basic', 'grant_verified', 'grant_certified', 'revoke_verification']

    @admin.action(description='Grant Basic (Level 1) verification')
    def grant_basic(self, request, queryset):
        for company in queryset:
            company.grant_verification(CompanyProfile.VerificationLevel.BASIC)

    @admin.action(description='Grant Verified (Level 2) verification')
    def grant_verified(self, request, queryset):
        for company in queryset:
            company.grant_verification(CompanyProfile.VerificationLevel.VERIFIED)

    @admin.action(description='Grant Certified (Level 3) verification')
    def grant_certified(self, request, queryset):
        for company in queryset:
            company.grant_verification(CompanyProfile.VerificationLevel.CERTIFIED)

    @admin.action(description='Revoke verification (set to Unverified)')
    def revoke_verification(self, request, queryset):
        for company in queryset:
            company.revoke_verification()


@admin.register(VerificationRequest)
class VerificationRequestAdmin(ModelAdmin):
    list_display = ['company', 'requested_level', 'status', 'created_at', 'reviewed_at']
    list_filter = ['status', 'requested_level']
    search_fields = ['company__company_name', 'company__owner__email']
    readonly_fields = ['company', 'requested_level', 'documents', 'note',
                       'reviewed_by', 'reviewed_at', 'created_at']
    actions = ['approve_requests', 'reject_requests']

    @admin.action(description='Approve selected requests (grants the tier)')
    def approve_requests(self, request, queryset):
        for req in queryset.filter(status=VerificationRequest.Status.PENDING):
            req.approve(reviewer=request.user, notes='Approved by admin.')

    @admin.action(description='Reject selected requests')
    def reject_requests(self, request, queryset):
        for req in queryset.filter(status=VerificationRequest.Status.PENDING):
            req.reject(reviewer=request.user, notes='Rejected by admin.')
