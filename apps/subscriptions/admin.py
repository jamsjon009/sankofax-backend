from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(ModelAdmin):
    list_display = ['name', 'tier_level', 'region', 'price', 'billing_cycle', 'max_listings', 'is_active']
    list_per_page = 10
    list_filter = ['region', 'billing_cycle', 'is_active']
    search_fields = ['name']
    ordering = ['tier_level', 'price']


@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ['user', 'plan', 'company', 'status', 'current_period_end', 'created_at']
    list_per_page = 10
    list_filter = ['status', 'plan']
    search_fields = ['user__email', 'company__company_name']
    readonly_fields = ['created_at']
