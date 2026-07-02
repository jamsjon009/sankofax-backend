from django.urls import path
from .views import PlanListView, SubscriptionListView, MySubscriptionView, BillingPortalView, CheckoutView, stripe_webhook

urlpatterns = [
    path('plans/', PlanListView.as_view(), name='plan-list'),
    path('subscriptions/', SubscriptionListView.as_view(), name='subscription-list'),
    path('subscriptions/my/', MySubscriptionView.as_view(), name='my-subscription'),
    path('subscriptions/checkout/', CheckoutView.as_view(), name='checkout'),
    path('subscriptions/portal/', BillingPortalView.as_view(), name='billing-portal'),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
]
