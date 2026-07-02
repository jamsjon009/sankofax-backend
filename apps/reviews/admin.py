from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Review


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ['listing', 'user', 'rating', 'status', 'created_at']
    list_filter = ['status', 'rating']
    search_fields = ['listing__title', 'user__email', 'title']
    actions = ['approve_reviews', 'flag_reviews', 'remove_reviews']

    @admin.action(description='Approve selected reviews')
    def approve_reviews(self, request, queryset):
        queryset.update(status=Review.Status.APPROVED)

    @admin.action(description='Flag selected reviews')
    def flag_reviews(self, request, queryset):
        queryset.update(status=Review.Status.FLAGGED)

    @admin.action(description='Remove selected reviews')
    def remove_reviews(self, request, queryset):
        queryset.update(status=Review.Status.REMOVED)
