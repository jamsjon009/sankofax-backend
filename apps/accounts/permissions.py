from rest_framework import permissions


class IsBusinessOwner(permissions.BasePermission):
    """Allow only business owners (or admins/staff) to act.

    Business features — creating a company, publishing listings, selling
    products/services — are reserved for the Business Owner role. Visitors must
    upgrade first (POST /api/auth/upgrade-to-business/). Admins and staff are
    always allowed so they can manage businesses on an owner's behalf.
    """
    message = (
        'Only business owners can do this. Upgrade your account to a business '
        'owner to list and manage a business.'
    )

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_business_owner or user.is_admin_or_staff)
        )
