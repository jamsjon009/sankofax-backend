from rest_framework import permissions


class HasAnalyticsAccess(permissions.BasePermission):
    """Staff, or a business owner on a plan with analytics access."""
    message = 'Analytics is available on plans with analytics access. Upgrade your subscription to unlock it.'

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.is_admin_or_staff:
            return True
        from apps.subscriptions.models import Subscription
        return Subscription.objects.filter(
            user=user,
            status__in=[Subscription.Status.ACTIVE, Subscription.Status.TRIALING],
            plan__analytics_access=True,
        ).exists()
