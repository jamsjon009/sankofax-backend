from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, serializers as drf_serializers
from django.core.mail import send_mail
from django.conf import settings as django_settings
from .models import SiteSetting, Page, FAQ, Testimonial


class ContactSerializer(drf_serializers.Serializer):
    name = drf_serializers.CharField(max_length=200)
    email = drf_serializers.EmailField()
    subject = drf_serializers.CharField(max_length=200, required=False, default='')
    message = drf_serializers.CharField()


class SiteSettingView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        site = SiteSetting.get()
        return Response({
            'site_name': site.site_name,
            'meta_description': site.meta_description,
            'footer_text': site.footer_text,
            # Contact
            'contact_email': site.contact_email,
            'contact_phone': site.contact_phone,
            'contact_address': site.contact_address,
            'response_time': site.response_time,
            'map_embed_code': site.map_embed_code,
            # Social
            'instagram_url': site.instagram_url,
            'facebook_url': site.facebook_url,
            'twitter_url': site.twitter_url,
            'linkedin_url': site.linkedin_url,
            'youtube_url': site.youtube_url,
            'tiktok_url': site.tiktok_url,
            'instagram_embed_code': site.instagram_embed_code,
            # Analytics
            'google_tag_manager_id': site.google_tag_manager_id,
            'google_analytics_id': site.google_analytics_id,
            'google_search_console_code': site.google_search_console_code,
        })


class PageDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        try:
            page = Page.objects.get(slug=slug, is_active=True)
            return Response({'title': page.title, 'content': page.content})
        except Page.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound()


class FAQListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        faqs = FAQ.objects.filter(is_active=True).order_by('order', 'id')
        return Response([{'question': f.question, 'answer': f.answer} for f in faqs])


class ContactView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        site = SiteSetting.get()
        recipient = site.contact_email or django_settings.DEFAULT_FROM_EMAIL

        subject_line = data.get('subject') or f'Contact from {data["name"]}'
        html = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:24px;">
          <h2 style="color:#1c1a17;">New Contact Message</h2>
          <table style="width:100%;border-collapse:collapse;">
            <tr><td style="padding:8px 0;color:#7a6a56;width:80px;"><strong>Name</strong></td><td>{data['name']}</td></tr>
            <tr><td style="padding:8px 0;color:#7a6a56;"><strong>Email</strong></td><td>{data['email']}</td></tr>
            <tr><td style="padding:8px 0;color:#7a6a56;"><strong>Subject</strong></td><td>{data.get('subject', '-')}</td></tr>
          </table>
          <hr style="margin:16px 0;border:none;border-top:1px solid #e8ddd0;">
          <p style="color:#2a2420;line-height:1.7;">{data['message']}</p>
          <hr style="margin:16px 0;border:none;border-top:1px solid #e8ddd0;">
          <p style="color:#b5813b;font-size:13px;font-weight:600;">SankofaX Admin</p>
        </div>
        """

        send_mail(
            subject=f'[SankofaX] {subject_line}',
            message=data['message'],
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            html_message=html,
            fail_silently=True,
        )

        # Save as CRM lead
        from apps.crm.models import Lead
        Lead.objects.get_or_create(
            email=data['email'],
            defaults={
                'name': data['name'],
                'subject': data.get('subject', ''),
                'message': data['message'],
                'source': Lead.Source.CONTACT_FORM,
            }
        )

        return Response({'sent': True})

class TestimonialListView(APIView):
    """Public: list approved testimonials."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        qs = Testimonial.objects.filter(status=Testimonial.Status.APPROVED)
        data = [
            {
                'id': t.id,
                'body': t.body,
                'role': t.role,
                'author': t.user.get_full_name() or t.user.email.split('@')[0],
                'initials': _initials(t.user.get_full_name() or t.user.email),
            }
            for t in qs
        ]
        return Response(data)


class TestimonialSubmitView(APIView):
    """Business owners submit a testimonial (one pending at a time)."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from apps.directory.models import Listing
        has_listing = Listing.objects.filter(
            company__owner=request.user,
            listing_status='published',
        ).exists()
        if not has_listing:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only business owners with a published listing can submit a testimonial.')

        if Testimonial.objects.filter(user=request.user, status=Testimonial.Status.PENDING).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError('You already have a testimonial pending review.')

        body = request.data.get('body', '').strip()
        role = request.data.get('role', '').strip()
        if not body or not role:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': 'body and role are required.'})
        if len(body) > 500:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'body': 'Max 500 characters.'})

        t = Testimonial.objects.create(user=request.user, body=body, role=role)
        return Response({'id': t.id, 'status': t.status}, status=201)

    def get(self, request):
        """Return the current user's testimonial (if any)."""
        t = Testimonial.objects.filter(user=request.user).order_by('-created_at').first()
        if not t:
            return Response(None)
        return Response({
            'id': t.id,
            'body': t.body,
            'role': t.role,
            'status': t.status,
            'created_at': t.created_at,
        })


def _initials(name: str) -> str:
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper()


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Avg


class IsStaffOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin_or_staff


class AdminStatsView(APIView):
    permission_classes = [IsStaffOrAdmin]

    def get(self, request):
        from apps.accounts.models import User
        from apps.directory.models import Listing
        from apps.reviews.models import Review
        from apps.newsletter.models import Subscriber
        from apps.crm.models import Lead
        from apps.blog.models import BlogPost

        now = timezone.now()
        last_7  = now - timedelta(days=7)
        last_30 = now - timedelta(days=30)

        # Users
        total_users        = User.objects.count()
        new_users_7d       = User.objects.filter(date_joined__gte=last_7).count()
        new_users_30d      = User.objects.filter(date_joined__gte=last_30).count()
        business_owners    = User.objects.filter(role='business_owner').count()
        verified_users     = User.objects.filter(is_verified=True).count()

        # Listings
        total_listings     = Listing.objects.count()
        published_listings = Listing.objects.filter(listing_status='published').count()
        pending_listings   = Listing.objects.filter(listing_status='pending_review').count()
        featured_listings  = Listing.objects.filter(featured=True).count()

        # Reviews
        total_reviews      = Review.objects.count()
        pending_reviews    = Review.objects.filter(status='pending').count()
        avg_rating         = Review.objects.filter(status='approved').aggregate(avg=Avg('rating'))['avg']

        # Newsletter
        total_subscribers  = Subscriber.objects.filter(is_active=True).count()
        new_subs_30d       = Subscriber.objects.filter(subscribed_at__gte=last_30).count()

        # CRM
        new_leads          = Lead.objects.filter(status='new').count()
        total_leads        = Lead.objects.count()

        # Blog
        published_posts    = BlogPost.objects.filter(status='published').count()
        draft_posts        = BlogPost.objects.filter(status='draft').count()

        return Response({
            'users': {
                'total': total_users,
                'new_7d': new_users_7d,
                'new_30d': new_users_30d,
                'business_owners': business_owners,
                'verified': verified_users,
            },
            'listings': {
                'total': total_listings,
                'published': published_listings,
                'pending': pending_listings,
                'featured': featured_listings,
            },
            'reviews': {
                'total': total_reviews,
                'pending': pending_reviews,
                'avg_rating': round(avg_rating, 2) if avg_rating else None,
            },
            'newsletter': {
                'subscribers': total_subscribers,
                'new_30d': new_subs_30d,
            },
            'crm': {
                'leads_total': total_leads,
                'leads_new': new_leads,
            },
            'blog': {
                'published': published_posts,
                'drafts': draft_posts,
            },
        })