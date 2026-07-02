from django.db import models
from django.conf import settings


class Plan(models.Model):
    class BillingCycle(models.TextChoices):
        MONTHLY = 'monthly', 'Monthly'
        ANNUAL = 'annual', 'Annual'
        ONE_TIME = 'one_time', 'One-Time'

    class Region(models.TextChoices):
        GLOBAL_NORTH = 'global_north', 'Global North'
        GLOBAL_SOUTH = 'global_south', 'Global South'

    name = models.CharField(max_length=100)
    tier_level = models.PositiveIntegerField(default=0, help_text='For sort order (0=lowest)')
    region = models.CharField(max_length=20, choices=Region.choices, blank=True, help_text='Leave blank for a single global price')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    billing_cycle = models.CharField(max_length=10, choices=BillingCycle.choices, default=BillingCycle.MONTHLY)
    max_listings = models.PositiveIntegerField(default=1)
    featured_listing_slots = models.PositiveIntegerField(default=0)
    analytics_access = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    stripe_price_id = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    features_list = models.JSONField(default=list, blank=True, help_text='List of feature strings shown on pricing page')

    class Meta:
        ordering = ['tier_level', 'price']

    def __str__(self):
        region_label = f' ({self.region})' if self.region else ''
        return f'{self.name}{region_label} — ${self.price}/{self.billing_cycle}'


class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        PAST_DUE = 'past_due', 'Past Due'
        CANCELED = 'canceled', 'Canceled'
        TRIALING = 'trialing', 'Trialing'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    company = models.ForeignKey('profiles.CompanyProfile', null=True, blank=True, on_delete=models.SET_NULL, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} → {self.plan.name} ({self.status})'
