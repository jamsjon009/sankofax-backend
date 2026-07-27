from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models import StoryPackage, StorySubmission


@admin.register(StoryPackage)
class StoryPackageAdmin(ModelAdmin):
    list_display = ['name', 'kind', 'price', 'currency', 'duration_days',
                    'subscriber_discount_percent', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    list_filter = ['kind', 'is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(StorySubmission)
class StorySubmissionAdmin(ModelAdmin):
    list_display = ['reference', 'title', 'company', 'kind', 'amount', 'currency',
                    'status', 'created_at']
    list_per_page = 25
    list_filter = ['status', 'kind']
    search_fields = ['reference', 'title', 'company__company_name', 'contact_email']
    readonly_fields = ['reference', 'package', 'company', 'submitted_by', 'kind', 'amount',
                       'currency', 'cover_preview', 'stripe_session_id', 'stripe_payment_intent',
                       'paid_at', 'published_post', 'featured_until', 'reviewed_by', 'reviewed_at',
                       'created_at', 'updated_at']
    actions = ['approve_and_publish', 'reject_selected']

    fieldsets = (
        (None, {'fields': ('reference', 'status', 'package', 'company', 'submitted_by', 'kind')}),
        ('Story', {'fields': ('title', 'body', 'cover_image', 'cover_preview', 'contact_email')}),
        ('Payment', {'fields': ('amount', 'currency', 'paid_at', 'stripe_session_id', 'stripe_payment_intent')}),
        ('Review', {'fields': ('admin_note', 'published_post', 'featured_until', 'reviewed_by', 'reviewed_at')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height:120px;border-radius:8px;">', obj.cover_image.url)
        return '-'
    cover_preview.short_description = 'Cover Preview'

    @admin.action(description='Approve & publish selected stories')
    def approve_and_publish(self, request, queryset):
        published = 0
        for sub in queryset:
            if sub.status in (StorySubmission.Status.IN_REVIEW, StorySubmission.Status.REJECTED):
                sub.publish(reviewer=request.user)
                published += 1
        self.message_user(request, f'{published} story(ies) published and featured.')

    @admin.action(description='Reject selected stories')
    def reject_selected(self, request, queryset):
        n = 0
        for sub in queryset.exclude(status=StorySubmission.Status.PUBLISHED):
            sub.reject(reviewer=request.user, note=sub.admin_note or 'Not approved for publication.')
            n += 1
        self.message_user(request, f'{n} submission(s) rejected.')
