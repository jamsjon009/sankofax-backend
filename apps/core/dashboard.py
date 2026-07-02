import json
from django.db.models import Count
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

    user_chart_labels, user_chart, listing_chart = [], [], []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        user_chart_labels.append(day.strftime('%b %d'))
        user_chart.append(User.objects.filter(date_joined__date=day.date()).count())
        listing_chart.append(Listing.objects.filter(created_at__date=day.date()).count())

    status_data = list(Listing.objects.values('listing_status').annotate(count=Count('id')))
    status_labels = [s['listing_status'].replace('_', ' ').title() for s in status_data]
    status_counts = [s['count'] for s in status_data]

    context.update({
        'kpi': [
            {'title': 'Pending Listings',     'value': Listing.objects.filter(listing_status='pending_review').count(), 'subtitle': 'Awaiting review',      'icon': 'pending',             'color': 'amber',   'bg': '#f59e0b', 'url': '/admin/directory/listing/?listing_status=pending_review'},
            {'title': 'Active Subscriptions', 'value': Subscription.objects.filter(status='active').count(),            'subtitle': 'Paying customers',      'icon': 'workspace_premium',   'color': 'emerald', 'bg': '#10b981', 'url': '/admin/subscriptions/subscription/'},
            {'title': 'New Users (7d)',        'value': User.objects.filter(date_joined__gte=week_ago).count(),          'subtitle': 'Last 7 days',           'icon': 'person_add',          'color': 'blue',    'bg': '#6366f1', 'url': '/admin/accounts/regularuserproxy/'},
            {'title': 'Open Tickets',          'value': SupportTicket.objects.filter(status='open').count(),             'subtitle': 'Need attention',        'icon': 'confirmation_number', 'color': 'red',     'bg': '#ef4444', 'url': '/admin/crm/supportticket/?status=open'},
            {'title': 'Newsletter Subs',       'value': Subscriber.objects.filter(is_active=True).count(),               'subtitle': 'Active subscribers',    'icon': 'mark_email_read',     'color': 'violet',  'bg': '#8b5cf6', 'url': '/admin/newsletter/subscriber/'},
            {'title': 'Live Listings',         'value': Listing.objects.filter(listing_status='published').count(),      'subtitle': 'Published on platform', 'icon': 'storefront',          'color': 'pink',    'bg': '#ec4899', 'url': '/admin/directory/listing/'},
        ],
        'recent_pending': list(
            Listing.objects.filter(listing_status='pending_review')
            .order_by('-created_at')[:8]
            .values('id', 'title', 'company__company_name', 'category__name', 'created_at')
        ),
        'new_leads': list(
            Lead.objects.filter(status='new').order_by('-created_at')[:6]
            .values('id', 'name', 'email', 'source', 'created_at')
        ),
        'open_tickets': list(
            SupportTicket.objects.filter(status='open').order_by('-created_at')[:6]
            .values('id', 'subject', 'priority', 'created_at')
        ),
        'chart_labels': json.dumps(user_chart_labels),
        'user_chart': json.dumps(user_chart),
        'listing_chart': json.dumps(listing_chart),
        'status_labels': json.dumps(status_labels),
        'status_counts': json.dumps(status_counts),
        'total_users': User.objects.count(),
        'total_companies': User.objects.filter(role='business_owner').count(),
    })
    return context
