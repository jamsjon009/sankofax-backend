from django_ckeditor_5.fields import CKEditor5Field
from django.db import models
from django.conf import settings


class SiteSetting(models.Model):
    site_name = models.CharField(max_length=100, default='SankofaX')
    logo = models.ImageField(upload_to='site/', null=True, blank=True)
    contact_email = models.EmailField(blank=True)
    footer_text = models.TextField(blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    default_og_image = models.ImageField(upload_to='site/', null=True, blank=True,
        help_text='Default social share image (1200×630px recommended)')

    # Contact info
    contact_phone   = models.CharField(max_length=30, blank=True,
        help_text='e.g. +1 (800) 726-5632 or +880 1711-000000')
    contact_address = models.CharField(max_length=300, blank=True,
        help_text='e.g. 123 Main St, Nairobi, Kenya')
    map_embed_code  = models.TextField(blank=True,
        help_text='Google Maps → Share → Embed a map → paste the full &lt;iframe&gt; code here')
    response_time   = models.CharField(max_length=100, blank=True, default='Within 24–48 hours',
        help_text='e.g. Within 24–48 hours')

    # Social links (structured)
    instagram_url  = models.URLField(blank=True,
        help_text='e.g. https://www.instagram.com/sankofax — footer icons will appear when URLs are added')
    facebook_url   = models.URLField(blank=True,
        help_text='e.g. https://www.facebook.com/sankofax')
    twitter_url    = models.URLField(blank=True,
        help_text='e.g. https://x.com/sankofax')
    linkedin_url   = models.URLField(blank=True,
        help_text='e.g. https://www.linkedin.com/company/sankofax')
    youtube_url    = models.URLField(blank=True,
        help_text='e.g. https://www.youtube.com/@sankofax')
    tiktok_url     = models.URLField(blank=True,
        help_text='e.g. https://www.tiktok.com/@sankofax')

    # Instagram feed (footer). Paste the embed code from a widget service such as
    # SnapWidget, LightWidget or Behold. When set, it replaces the placeholder tiles.
    instagram_embed_code = models.TextField(blank=True,
        help_text='Footer Instagram feed. Get an embed code from snapwidget.com or lightwidget.com '
                  '(connect your Instagram there, copy the <iframe> embed) and paste it here. '
                  'Leave blank to show the default placeholder tiles.')

    # Tag / Analytics
    google_tag_manager_id = models.CharField(max_length=20, blank=True,
        help_text='Google Tag Manager ID — e.g. GTM-XXXXXXX')
    google_analytics_id = models.CharField(max_length=30, blank=True,
        help_text='GA4 Measurement ID — e.g. G-XXXXXXXXXX (leave blank if using GTM)')
    google_search_console_code = models.CharField(max_length=200, blank=True,
        help_text='Google Search Console verification meta content value')

    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = CKEditor5Field(config_name='default')
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField(max_length=300)
    answer = CKEditor5Field(config_name='minimal')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question


class PageView(models.Model):
    class DeviceType(models.TextChoices):
        DESKTOP = 'desktop', 'Desktop'
        MOBILE  = 'mobile',  'Mobile'
        TABLET  = 'tablet',  'Tablet'
        BOT     = 'bot',     'Bot'
        OTHER   = 'other',   'Other'

    path         = models.CharField(max_length=500)
    browser      = models.CharField(max_length=60, blank=True)   # Chrome, Firefox, Safari…
    browser_ver  = models.CharField(max_length=20, blank=True)
    os           = models.CharField(max_length=60, blank=True)   # Windows, macOS, Android…
    device_type  = models.CharField(max_length=10, choices=DeviceType.choices, default=DeviceType.OTHER)
    country      = models.CharField(max_length=80, blank=True)   # from CF-IPCountry or X-Country
    ip_hash      = models.CharField(max_length=64, blank=True)   # hashed for privacy
    referrer     = models.CharField(max_length=500, blank=True)
    session_key  = models.CharField(max_length=64, blank=True)   # for unique visitor approx.
    timestamp    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['browser']),
            models.Index(fields=['country']),
            models.Index(fields=['path']),
        ]

    def __str__(self):
        return f'{self.path} — {self.browser} ({self.timestamp:%Y-%m-%d})'


class Testimonial(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='testimonials',
    )
    body = models.TextField(help_text='The testimonial text (max ~300 chars recommended)')
    role = models.CharField(max_length=150, help_text='E.g. "Business Owner – Accra, Ghana"')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    order = models.PositiveIntegerField(default=0, help_text='Lower = shown first')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f'{self.user.email} — {self.status}'
