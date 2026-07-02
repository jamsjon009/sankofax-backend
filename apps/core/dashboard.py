"""
Unfold admin dashboard callbacks — registered in settings.UNFOLD['DASHBOARD_CALLBACK'].
Returns context data rendered into the admin index page.
"""
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta


def pending_listings_badge(request):
    from apps.directory.models import Listing
    count = Listing.objects.filter(listing_status='pending_review').count()
    return str(count) if count else None


def dashboard_callback(request, context):
    from apps.directory.models import Listing
    from apps.accounts.models import User
    from apps.subscriptions.models import Subscription
    from apps.newsletter.models import Subscriber
    from apps.crm.models import Lead, SupportTicket

    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Key metrics
    context.update({
        'kpi': [
            {
                'title': 'Pending Listings',
                'value': Listing.objects.filter(listing_status='pending_review').count(),
                'subtitle': 'Awaiting review',
                'color': 'amber',
                'url': '/admin/directory/listing/?listing_status=pending_review',
            },
            {
                'title': 'Active Subscriptions',
                'value': Subscription.objects.filter(status='active').count(),
                'subtitle': 'Paying customers',
                'color': 'green',
                'url': '/admin/subscriptions/subscription/',
            },
            {
                'title': 'New Users (7d)',
                'value': User.objects.filter(date_joined__gte=week_ago).count(),
                'subtitle': 'Last 7 days',
                'color': 'blue',
                'url': '/admin/accounts/user/',
            },
            {
                'title': 'Open Tickets',
                'value': SupportTicket.objects.filter(status='open').count(),
                'subtitle': 'Need attention',
                'color': 'red',
                'url': '/admin/crm/supportticket/?status=open',
            },
            {
                'title': 'Subscribers',
                'value': Subscriber.objects.filter(is_active=True).count(),
                'subtitle': 'Newsletter list',
                'color': 'purple',
                'url': '/admin/newsletter/subscriber/',
            },
            {
                'title': 'Total Listings',
                'value': Listing.objects.filter(listing_status='published').count(),
                'subtitle': 'Live on the platform',
                'color': 'emerald',
                'url': '/admin/directory/listing/',
            },
        ],
        'recent_pending': list(
            Listing.objects.filter(listing_status='pending_review')
            .select_related('company', 'category')
            .order_by('-created_at')[:8]
            .values('id', 'title', 'company__company_name', 'category__name', 'created_at')
        ),
        'new_leads': list(
            Lead.objects.filter(status='new')
            .order_by('-created_at')[:6]
            .values('id', 'name', 'email', 'source', 'created_at')
        ),
        'open_tickets': list(
            SupportTicket.objects.filter(status='open')
            .order_by('-created_at')[:6]
            .values('id', 'subject', 'priority', 'created_at')
        ),
    })
    return context
