"""Owner-scoped analytics aggregation across the platform's apps.

Everything is scoped to the companies a user owns (staff may pass any company slug).
Metrics come from real per-company signals: listing views/saves/reviews, connections,
event registrations, marketplace orders/bookings, and story promotions.
"""
from datetime import timedelta

from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import TruncDate
from django.utils import timezone


def resolve_companies(user, company_slug=None):
    """Companies in scope for this user (all owned, or one by slug). Staff may target any."""
    from apps.profiles.models import CompanyProfile
    qs = CompanyProfile.objects.all() if user.is_admin_or_staff else CompanyProfile.objects.filter(owner=user)
    if company_slug:
        qs = qs.filter(slug=company_slug)
    return list(qs)


def _decimal(value):
    return str(value if value is not None else 0)


def build_summary(companies, days=30):
    from apps.directory.models import Listing
    from apps.reviews.models import Review
    from apps.connections.models import Connection
    from apps.events.models import EventRegistration
    from apps.marketplace.models import Order, ServiceBooking
    from apps.promotions.models import StorySubmission

    company_ids = [c.id for c in companies]
    since = timezone.now() - timedelta(days=days)

    listings = Listing.objects.filter(company_id__in=company_ids)
    published = listings.filter(listing_status='published')

    per_listing = list(
        published.annotate(saves=Count('saved_by', distinct=True))
        .values('title', 'slug', 'view_count', 'review_count', 'avg_rating', 'featured', 'saves')
        .order_by('-view_count')[:20]
    )

    reviews = Review.objects.filter(listing__company_id__in=company_ids)
    approved_reviews = reviews.filter(status='approved')

    # Engagement
    connections = Connection.objects.filter(listing__company_id__in=company_ids)
    registrations = EventRegistration.objects.filter(event__organizer_id__in=company_ids)
    confirmed_regs = registrations.filter(status='confirmed')

    # Commerce (windowed)
    orders = Order.objects.filter(company_id__in=company_ids)
    orders_window = orders.filter(created_at__gte=since)
    paid_orders = orders.filter(status__in=['paid', 'fulfilled'])
    revenue = paid_orders.aggregate(s=Sum('total'))['s'] or 0

    bookings = ServiceBooking.objects.filter(company_id__in=company_ids)
    bookings_window = bookings.filter(created_at__gte=since)

    submissions = StorySubmission.objects.filter(company_id__in=company_ids)

    return {
        'companies': [{'slug': c.slug, 'name': c.company_name,
                       'verification_level': getattr(c, 'verification_level', 0),
                       'is_verified': getattr(c, 'is_verified', False)} for c in companies],
        'window_days': days,
        'listings': {
            'published': published.count(),
            'total': listings.count(),
            'total_views': published.aggregate(s=Sum('view_count'))['s'] or 0,
            'total_saves': published.aggregate(s=Count('saved_by'))['s'] or 0,
            'featured': published.filter(featured=True).count(),
            'by_listing': per_listing,
        },
        'reviews': {
            'total': reviews.count(),
            'approved': approved_reviews.count(),
            'pending': reviews.filter(status='pending').count(),
            'avg_rating': round(approved_reviews.aggregate(a=Avg('rating'))['a'], 2)
                          if approved_reviews.exists() else None,
        },
        'engagement': {
            'connections_received': connections.count(),
            'connections_accepted': connections.filter(status='accepted').count(),
            'event_registrations': registrations.exclude(status='cancelled').count(),
            'tickets_sold': confirmed_regs.aggregate(s=Sum('quantity'))['s'] or 0,
        },
        'commerce': {
            'orders_total': orders.count(),
            f'orders_last_{days}d': orders_window.count(),
            'paid_orders': paid_orders.count(),
            'revenue': _decimal(revenue),
            'bookings_total': bookings.count(),
            f'bookings_last_{days}d': bookings_window.count(),
            'bookings_confirmed': bookings.filter(status__in=['confirmed', 'completed']).count(),
        },
        'promotions': {
            'submissions': submissions.count(),
            'published': submissions.filter(status='published').count(),
            'in_review': submissions.filter(status='in_review').count(),
        },
        'traffic': _traffic_breakdown(companies, days),
    }


def _traffic_breakdown(companies, days):
    """Best-effort device/country/referrer split from PageView rows whose path
    references one of the companies' listing slugs. Sparse in a split frontend/backend
    deployment, so we also return a note."""
    from apps.core.models import PageView
    from apps.directory.models import Listing

    slugs = list(Listing.objects.filter(company__in=companies).values_list('slug', flat=True))
    since = timezone.now() - timedelta(days=days)
    q = Q()
    for s in slugs:
        q |= Q(path__contains=s)
    views = PageView.objects.filter(timestamp__gte=since).filter(q) if slugs else PageView.objects.none()

    def top(field, limit=5):
        return list(views.exclude(**{f'{field}': ''})
                    .values(field).annotate(n=Count('id')).order_by('-n')[:limit])

    total = views.count()
    return {
        'tracked_views': total,
        'by_device': top('device_type'),
        'by_country': top('country'),
        'by_referrer': top('referrer'),
        'note': None if total else 'Detailed traffic tracking is limited in this deployment; '
                                   'listing view counts above are the primary view metric.',
    }


# --- Time series ------------------------------------------------------------

TIMESERIES_SOURCES = {
    'orders': ('apps.marketplace.models', 'Order', 'created_at', 'company_id__in', 'total'),
    'bookings': ('apps.marketplace.models', 'ServiceBooking', 'created_at', 'company_id__in', 'total'),
    'reviews': ('apps.reviews.models', 'Review', 'created_at', 'listing__company_id__in', None),
    'registrations': ('apps.events.models', 'EventRegistration', 'created_at', 'event__organizer_id__in', None),
    'connections': ('apps.connections.models', 'Connection', 'created_at', 'listing__company_id__in', None),
}


def build_timeseries(companies, metric, days=30):
    import importlib
    if metric not in TIMESERIES_SOURCES:
        return None
    module_path, model_name, date_field, filter_key, sum_field = TIMESERIES_SOURCES[metric]
    model = getattr(importlib.import_module(module_path), model_name)
    company_ids = [c.id for c in companies]
    since = timezone.now() - timedelta(days=days)

    qs = model.objects.filter(**{filter_key: company_ids, f'{date_field}__gte': since})
    agg = {'count': Count('id')}
    if sum_field:
        agg['total'] = Sum(sum_field)
    rows = (qs.annotate(date=TruncDate(date_field))
            .values('date').annotate(**agg).order_by('date'))
    return [
        {'date': r['date'].isoformat(), 'count': r['count'],
         **({'total': _decimal(r.get('total'))} if sum_field else {})}
        for r in rows
    ]


# --- Export -----------------------------------------------------------------

EXPORT_DATASETS = {
    'listings': {
        'model': ('apps.directory.models', 'Listing'),
        'filter': 'company_id__in',
        'columns': ['slug', 'title', 'listing_status', 'view_count', 'review_count',
                    'avg_rating', 'featured', 'created_at'],
    },
    'reviews': {
        'model': ('apps.reviews.models', 'Review'),
        'filter': 'listing__company_id__in',
        'columns': ['id', 'listing__title', 'rating', 'title', 'status', 'created_at'],
    },
    'orders': {
        'model': ('apps.marketplace.models', 'Order'),
        'filter': 'company_id__in',
        'columns': ['order_number', 'status', 'total', 'currency', 'contact_name',
                    'contact_email', 'created_at', 'paid_at'],
    },
    'bookings': {
        'model': ('apps.marketplace.models', 'ServiceBooking'),
        'filter': 'company_id__in',
        'columns': ['booking_number', 'service_name', 'status', 'total', 'currency',
                    'contact_name', 'contact_email', 'scheduled_for', 'created_at'],
    },
    'registrations': {
        'model': ('apps.events.models', 'EventRegistration'),
        'filter': 'event__organizer_id__in',
        'columns': ['ticket_code', 'event__title', 'name', 'email', 'quantity',
                    'status', 'checked_in', 'created_at'],
    },
    'connections': {
        'model': ('apps.connections.models', 'Connection'),
        'filter': 'listing__company_id__in',
        'columns': ['kind', 'subject', 'sender__email', 'listing__title', 'status', 'created_at'],
    },
}


def export_rows(companies, dataset):
    """Return (columns, iterator-of-row-dicts) for the requested dataset."""
    import importlib
    cfg = EXPORT_DATASETS[dataset]
    module_path, model_name = cfg['model']
    model = getattr(importlib.import_module(module_path), model_name)
    company_ids = [c.id for c in companies]
    columns = cfg['columns']
    qs = model.objects.filter(**{cfg['filter']: company_ids}).values(*columns).order_by('-created_at')
    return columns, qs
