from rest_framework import serializers
from .models import Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            'id', 'name', 'tier_level', 'region', 'price', 'currency', 'billing_cycle',
            'max_listings', 'featured_listing_slots', 'analytics_access',
            'priority_support', 'description', 'features_list',
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'plan', 'status', 'current_period_end', 'stripe_customer_id', 'created_at']


class CheckoutSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()
    company_id = serializers.UUIDField(required=False)
