import json
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta


def pending_listings_badge(request):
    from apps.directory.models import Listing
    count = Listing.objects.filter(listing_status='pending_review').count()
    return str(count) if count else None


def pending_testimonials_badge(request):
    from apps.core.models import Testimonial
    count = Testimonial.objects.filter(status='pending').count()
    return str(count) if count else None


def dashboard_callback(request, context):
    from apps.directory.models import Listing, Category
    from apps.accounts.models import User
    from apps.subscriptions.models import Subscription
    from apps.newsletter.models import Subscriber
    from apps.crm.models import Lead, SupportTicket
    from apps.blog.models import BlogPost
    from apps.core.models import Testimonial, PageView
    from django.db.models import Sum, F

    now = timezone.now()
    week_ago  = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # 7-day chart data
    user_chart_labels, user_chart, listing_chart = [], [], []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        user_chart_labels.append(day.strftime('%b %d'))
        user_chart.append(User.objects.filter(date_joined__date=day.date()).count())
        listing_chart.append(Listing.objects.filter(created_at__date=day.date()).count())

    status_data = list(Listing.objects.values('listing_status').annotate(count=Count('id')))
    status_labels = [s['listing_status'].replace('_', ' ').title() for s in status_data]
    status_counts = [s['count'] for s in status_data]

    # Blog
    blog_published = BlogPost.objects.filter(status='published').count()
    blog_drafts    = BlogPost.objects.filter(status='draft').count()

    # Testimonials
    testimonials_pending  = Testimonial.objects.filter(status='pending').count()
    testimonials_approved = Testimonial.objects.filter(status='approved').count()

    # ── PageView Analytics ───────────────────────────────────────────
    pv_total_7d   = PageView.objects.filter(timestamp__gte=week_ago).count()
    pv_total_30d  = PageView.objects.filter(timestamp__gte=month_ago).count()
    pv_today      = PageView.objects.filter(timestamp__date=now.date()).count()

    top_browsers = list(
        PageView.objects.filter(timestamp__gte=month_ago)
        .exclude(browser='').values('browser')
        .annotate(count=Count('id')).order_by('-count')[:8]
    )
    top_pages = list(
        PageView.objects.filter(timestamp__gte=month_ago)
        .values('path').annotate(count=Count('id')).order_by('-count')[:8]
    )
    pv_by_country = list(
        PageView.objects.filter(timestamp__gte=month_ago)
        .exclude(country='').values('country')
        .annotate(count=Count('id')).order_by('-count')[:8]
    )
    pv_by_device = list(
        PageView.objects.filter(timestamp__gte=month_ago)
        .values('device_type').annotate(count=Count('id')).order_by('-count')
    )
    pv_by_os = list(
        PageView.objects.filter(timestamp__gte=month_ago)
        .exclude(os='').values('os').annotate(count=Count('id')).order_by('-count')[:5]
    )

    # Daily pageviews chart (last 14 days)
    pv_chart_labels, pv_chart_data = [], []
    for i in range(13, -1, -1):
        day = now - timedelta(days=i)
        pv_chart_labels.append(day.strftime('%b %d'))
        pv_chart_data.append(PageView.objects.filter(timestamp__date=day.date()).count())

    max_browser = top_browsers[0]['count'] if top_browsers else 1
    max_pv_country = pv_by_country[0]['count'] if pv_by_country else 1
    max_page = top_pages[0]['count'] if top_pages else 1

    # ── Traffic Analytics ────────────────────────────────────────────
    published_qs = Listing.objects.filter(listing_status='published')
    total_listing_views = published_qs.aggregate(s=Sum('view_count'))['s'] or 0
    total_blog_views    = BlogPost.objects.filter(status='published').aggregate(s=Sum('view_count'))['s'] or 0
    total_views         = total_listing_views + total_blog_views

    top_listings = list(
        published_qs.order_by('-view_count')[:8]
        .values('id', 'title', 'view_count', 'category__name', 'country', 'slug')
    )
    top_blog_posts = list(
        BlogPost.objects.filter(status='published').order_by('-view_count')[:6]
        .values('id', 'title', 'view_count', 'slug')
    )
    views_by_country = list(
        published_qs.exclude(country='').values('country')
        .annotate(views=Sum('view_count'), listings=Count('id'))
        .order_by('-views')[:8]
    )
    views_by_category = list(
        published_qs.values('category__name')
        .annotate(views=Sum('view_count'), listings=Count('id'))
        .order_by('-views')[:6]
    )

    # 7-day listing views chart (daily view_count snapshots not stored — use created_at as proxy)
    view_chart_labels, view_chart_data = [], []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        view_chart_labels.append(day.strftime('%b %d'))
        view_chart_data.append(
            Listing.objects.filter(created_at__date=day.date()).aggregate(s=Sum('view_count'))['s'] or 0
        )

    max_listing_views = top_listings[0]['view_count'] if top_listings else 1

    # ── SEO Analytics ────────────────────────────────────────────────
    total_published   = published_qs.count()
    seo_with_title    = published_qs.exclude(meta_title='').count()
    seo_with_desc     = published_qs.exclude(meta_description='').count()
    seo_with_og       = published_qs.exclude(og_image=None).exclude(og_image='').count()
    seo_missing_title = total_published - seo_with_title
    seo_missing_desc  = total_published - seo_with_desc
    seo_score         = round(((seo_with_title + seo_with_desc + seo_with_og) / max((total_published * 3), 1)) * 100)
    seo_missing_og    = total_published - seo_with_og

    blog_total      = BlogPost.objects.filter(status='published').count()
    blog_seo_title  = BlogPost.objects.filter(status='published').exclude(meta_title='').count()
    blog_seo_desc   = BlogPost.objects.filter(status='published').exclude(meta_description='').count()

    seo_issues = list(
        published_qs.filter(meta_title='')
        .values('id', 'title', 'slug', 'category__name', 'view_count')
        .order_by('-view_count')[:8]
    )

    # Users
    unverified_users = User.objects.filter(is_verified=False, is_superuser=False).count()

    context.update({
        'kpi': [
            {'title': 'Pending Listings',     'value': Listing.objects.filter(listing_status='pending_review').count(),   'subtitle': 'Awaiting review',      'icon': 'pending',             'color': 'amber',   'bg': '#f59e0b', 'url': '/admin/directory/listing/?listing_status=pending_review'},
            {'title': 'Active Subscriptions', 'value': Subscription.objects.filter(status='active').count(),              'subtitle': 'Paying customers',      'icon': 'workspace_premium',   'color': 'emerald', 'bg': '#10b981', 'url': '/admin/subscriptions/subscription/'},
            {'title': 'New Users (7d)',        'value': User.objects.filter(date_joined__gte=week_ago).count(),            'subtitle': 'Last 7 days',           'icon': 'person_add',          'color': 'blue',    'bg': '#6366f1', 'url': '/admin/accounts/regularuserproxy/'},
            {'title': 'Open Tickets',          'value': SupportTicket.objects.filter(status='open').count(),               'subtitle': 'Need attention',        'icon': 'confirmation_number', 'color': 'red',     'bg': '#ef4444', 'url': '/admin/crm/supportticket/?status=open'},
            {'title': 'Newsletter Subs',       'value': Subscriber.objects.filter(is_active=True).count(),                 'subtitle': 'Active subscribers',    'icon': 'mark_email_read',     'color': 'violet',  'bg': '#8b5cf6', 'url': '/admin/newsletter/subscriber/'},
            {'title': 'Live Listings',         'value': Listing.objects.filter(listing_status='published').count(),        'subtitle': 'Published on platform', 'icon': 'storefront',          'color': 'pink',    'bg': '#ec4899', 'url': '/admin/directory/listing/'},
            {'title': 'Blog Posts',            'value': blog_published,                                                    'subtitle': f'{blog_drafts} drafts', 'icon': 'article',             'color': 'teal',    'bg': '#14b8a6', 'url': '/admin/blog/blogpost/'},
            {'title': 'Unverified Users',      'value': unverified_users,                                                  'subtitle': 'Email not confirmed',   'icon': 'mark_email_unread',   'color': 'orange',  'bg': '#f97316', 'url': '/admin/accounts/regularuserproxy/?is_verified__exact=0'},
            {'title': 'Pending Testimonials',  'value': testimonials_pending,                                               'subtitle': f'{testimonials_approved} approved', 'icon': 'rate_review', 'color': 'cyan', 'bg': '#06b6d4', 'url': '/admin/core/testimonial/?status=pending'},
        ],

        # Tables
        'recent_pending': list(
            Listing.objects.filter(listing_status='pending_review')
            .order_by('-created_at')[:8]
            .values('id', 'title', 'company__company_name', 'category__name', 'created_at')
        ),
        'new_leads': list(
            Lead.objects.filter(status='new').order_by('-created_at')[:6]
            .values('id', 'name', 'email', 'source', 'subject', 'created_at')
        ),
        'open_tickets': list(
            SupportTicket.objects.filter(status='open').order_by('-created_at')[:6]
            .values('id', 'subject', 'priority', 'created_at')
        ),
        'recent_subscribers': list(
            Subscriber.objects.filter(is_active=True).order_by('-subscribed_at')[:6]
            .values('email', 'source', 'subscribed_at')
        ),
        'recent_blog_posts': list(
            BlogPost.objects.order_by('-created_at')[:6]
            .values('id', 'title', 'status', 'is_featured', 'view_count', 'published_at')
        ),
        'pending_testimonials': list(
            Testimonial.objects.filter(status='pending').order_by('-created_at')[:8]
            .values('id', 'user__email', 'body', 'role', 'created_at')
        ),
        'recent_users': list(
            User.objects.filter(is_superuser=False).order_by('-date_joined')[:6]
            .values('id', 'email', 'role', 'is_verified', 'country', 'date_joined')
        ),

        # Charts
        'chart_labels':   json.dumps(user_chart_labels),
        'user_chart':     json.dumps(user_chart),
        'listing_chart':  json.dumps(listing_chart),
        'status_labels':  json.dumps(status_labels),
        'status_counts':  json.dumps(status_counts),

        # Totals
        'total_users':     User.objects.count(),
        'total_companies': User.objects.filter(role='business_owner').count(),
        'blog_published':  blog_published,
        'blog_drafts':     blog_drafts,
        'unverified_users': unverified_users,
        'new_leads_30d':   Lead.objects.filter(created_at__gte=month_ago).count(),

        # PageView Analytics
        'pv_total_7d':          pv_total_7d,
        'pv_total_30d':         pv_total_30d,
        'pv_today':             pv_today,
        'top_browsers':         top_browsers,
        'top_pages':            top_pages,
        'pv_by_country':        pv_by_country,
        'pv_by_device':         pv_by_device,
        'pv_by_os':             pv_by_os,
        'pv_chart_labels':      json.dumps(pv_chart_labels),
        'pv_chart_data':        json.dumps(pv_chart_data),
        'max_browser':          max_browser,
        'max_pv_country':       max_pv_country,
        'max_page':             max_page,

        # Traffic
        'total_views':          total_views,
        'total_listing_views':  total_listing_views,
        'total_blog_views':     total_blog_views,
        'top_listings':         top_listings,
        'top_blog_posts':       top_blog_posts,
        'views_by_country':     views_by_country,
        'views_by_category':    views_by_category,
        'max_listing_views':    max_listing_views or 1,
        'view_chart_labels':    json.dumps(view_chart_labels),
        'view_chart_data':      json.dumps(view_chart_data),

        # SEO
        'seo_score':            seo_score,
        'seo_with_title':       seo_with_title,
        'seo_with_desc':        seo_with_desc,
        'seo_with_og':          seo_with_og,
        'seo_missing_title':    seo_missing_title,
        'seo_missing_desc':     seo_missing_desc,
        'total_published':      total_published,
        'blog_total':           blog_total,
        'blog_seo_title':       blog_seo_title,
        'blog_seo_desc':        blog_seo_desc,
        'seo_missing_og':       seo_missing_og,
        'seo_issues':           seo_issues,
    })
    return context