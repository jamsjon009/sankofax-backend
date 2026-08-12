from django_ckeditor_5.fields import CKEditor5Field
import uuid
from django.db import models
from django.conf import settings
from django.utils.text import slugify


def unique_slug(model_class, value, slug_field='slug'):
    slug = slugify(value)
    base = slug
    n = 1
    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f'{base}-{n}'
        n += 1
    return slug


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    saved_listings = models.ManyToManyField(
        'directory.Listing', blank=True, related_name='saved_by'
    )

    def __str__(self):
        return f'Profile: {self.user.email}'


class IdentityBadge(models.Model):
    """Ownership / identity tag for a business, e.g. Women-Owned, Black-Owned, LGBTQ+-Owned."""
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True, max_length=100)
    icon = models.CharField(max_length=40, blank=True,
        help_text='Optional emoji or icon name shown with the badge, e.g. ♀ or a lucide icon name')
    color = models.CharField(max_length=7, blank=True,
        help_text='Optional hex colour for the badge, e.g. #B5813B')
    description = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0, help_text='Lower = shown first')

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Identity Badge'
        verbose_name_plural = 'Identity Badges'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(IdentityBadge, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CompanyProfile(models.Model):
    class Size(models.TextChoices):
        SOLO = 'solo', 'Solo'
        SMALL = '1-10', '1–10 employees'
        MEDIUM = '11-50', '11–50 employees'
        LARGE = '51+', '51+ employees'

    class VerificationLevel(models.IntegerChoices):
        NONE = 0, 'Unverified'
        BASIC = 1, 'Basic (Automated)'
        VERIFIED = 2, 'Verified (Documents)'
        CERTIFIED = 3, 'Certified (Partner)'

    # Automated Level-1 checks: (field key, human label). All must pass to grant Basic.
    AUTOMATED_CHECKS = [
        ('website', 'Business website provided'),
        ('contact_email', 'Contact email provided'),
        ('logo', 'Logo uploaded'),
        ('description', 'Business description added'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='companies')
    company_name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='covers/', null=True, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    company_size = models.CharField(max_length=10, choices=Size.choices, default=Size.SOLO)
    description = CKEditor5Field(config_name='minimal', blank=True)
    founder_story = models.TextField(blank=True,
        help_text="The founder's journey — how and why the business started. Shown on the business profile.")
    website = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)

    # Services offered (comma-separated), e.g. "Catering, Private events, Delivery"
    services = models.TextField(blank=True, help_text='Comma-separated list of services offered')

    # Social links
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)

    is_verified = models.BooleanField(default=False,
        help_text='Kept in sync with verification_level (True when level ≥ Basic).')
    verification_level = models.PositiveSmallIntegerField(
        choices=VerificationLevel.choices, default=VerificationLevel.NONE,
        help_text='Current verification tier. Granted automatically (Basic) or by admin review (Verified/Certified).')
    verified_at = models.DateTimeField(null=True, blank=True,
        help_text='When the current verification tier was granted.')
    verification_expires_at = models.DateTimeField(null=True, blank=True,
        help_text='When the current tier expires and needs re-verification.')
    verification_documents = models.FileField(upload_to='verifications/', null=True, blank=True)
    badges = models.ManyToManyField(IdentityBadge, blank=True, related_name='companies',
        help_text='Ownership / identity badges, e.g. Women-Owned, Black-Owned, LGBTQ+-Owned')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(CompanyProfile, self.company_name)
        super().save(*args, **kwargs)

    @property
    def services_list(self):
        return [s.strip() for s in self.services.split(',') if s.strip()]

    @property
    def social_links(self):
        links = {
            'instagram': self.instagram_url,
            'facebook': self.facebook_url,
            'twitter': self.twitter_url,
            'linkedin': self.linkedin_url,
            'youtube': self.youtube_url,
            'tiktok': self.tiktok_url,
        }
        return {k: v for k, v in links.items() if v}

    # ---- Verification ------------------------------------------------------

    def automated_check_results(self):
        """Level-1 automated checks — which profile signals are present."""
        from django.utils.html import strip_tags
        return {
            'website': bool(self.website),
            'contact_email': bool(self.contact_email),
            'logo': bool(self.logo),
            'description': bool(strip_tags(self.description or '').strip()),
        }

    def passes_automated_checks(self):
        return all(self.automated_check_results().values())

    @property
    def verification_label(self):
        return self.get_verification_level_display()

    @property
    def is_verification_expired(self):
        from django.utils import timezone
        return bool(self.verification_expires_at and self.verification_expires_at < timezone.now())

    def grant_verification(self, level, duration_days=365):
        """Grant a verification tier and keep is_verified in sync."""
        from django.utils import timezone
        from datetime import timedelta
        now = timezone.now()
        self.verification_level = level
        self.verified_at = now
        self.verification_expires_at = now + timedelta(days=duration_days) if level else None
        self.is_verified = level >= self.VerificationLevel.BASIC
        self.save(update_fields=[
            'verification_level', 'verified_at', 'verification_expires_at', 'is_verified',
        ])

    def revoke_verification(self):
        self.verification_level = self.VerificationLevel.NONE
        self.verified_at = None
        self.verification_expires_at = None
        self.is_verified = False
        self.save(update_fields=[
            'verification_level', 'verified_at', 'verification_expires_at', 'is_verified',
        ])


class VerificationRequest(models.Model):
    """A business owner's request to be granted a verification tier.

    Level 1 (Basic) is auto-resolved from automated checks. Levels 2 (Verified,
    document review) and 3 (Certified, partner-certified) are reviewed by an admin.
    """
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending review'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    company = models.ForeignKey(
        CompanyProfile, on_delete=models.CASCADE, related_name='verification_requests')
    requested_level = models.PositiveSmallIntegerField(
        choices=CompanyProfile.VerificationLevel.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    documents = models.FileField(upload_to='verifications/', null=True, blank=True,
        help_text='Ownership / registration documents (required for Verified and Certified).')
    note = models.TextField(blank=True, help_text="Owner's note to the reviewer.")
    admin_notes = models.TextField(blank=True,
        help_text='Reviewer notes / reason — shown to the business owner.')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reviewed_verifications')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Verification Request'
        verbose_name_plural = 'Verification Requests'

    def __str__(self):
        return f'{self.company.company_name} → L{self.requested_level} ({self.status})'

    @property
    def requested_level_label(self):
        return CompanyProfile.VerificationLevel(self.requested_level).label

    def approve(self, reviewer=None, notes=''):
        from django.utils import timezone
        self.status = self.Status.APPROVED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        if notes:
            self.admin_notes = notes
        self.save()
        self.company.grant_verification(self.requested_level)

    def reject(self, reviewer=None, notes=''):
        from django.utils import timezone
        self.status = self.Status.REJECTED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        if notes:
            self.admin_notes = notes
        self.save()
