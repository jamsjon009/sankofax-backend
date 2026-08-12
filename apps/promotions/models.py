import re
import uuid
from decimal import Decimal, ROUND_HALF_UP
from datetime import timedelta

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify


def unique_slug(model_class, value, slug_field='slug'):
    slug = slugify(value) or 'package'
    base = slug
    n = 1
    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f'{base}-{n}'
        n += 1
    return slug


# Which blog category a published story lands in, by package kind.
KIND_CATEGORY = {
    'founder_story': 'success-stories',
    'brand_feature': 'success-stories',
    'press_release': 'diaspora-news',
}


class StoryPackage(models.Model):
    """A purchasable story-promotion product (founder story, brand feature, press release)."""

    class Kind(models.TextChoices):
        FOUNDER_STORY = 'founder_story', 'Founder Story'
        BRAND_FEATURE = 'brand_feature', 'Brand Feature'
        PRESS_RELEASE = 'press_release', 'Press Release'

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, max_length=140)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.FOUNDER_STORY)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    duration_days = models.PositiveIntegerField(default=30,
        help_text='How long the published story stays featured.')
    subscriber_discount_percent = models.PositiveSmallIntegerField(default=0,
        help_text='Discount (%) applied when the buyer has an active subscription.')
    description = models.CharField(max_length=250, blank=True)
    features_list = models.JSONField(default=list, blank=True,
        help_text='Bullet points shown on the package card.')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text='Lower = shown first')

    class Meta:
        ordering = ['order', 'price']

    def __str__(self):
        return f'{self.name} — {self.currency} {self.price}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(StoryPackage, self.name)
        super().save(*args, **kwargs)

    def price_for(self, user):
        """Price after any active-subscriber discount."""
        price = self.price
        if self.subscriber_discount_percent and user and user.is_authenticated:
            from apps.subscriptions.models import Subscription
            has_sub = Subscription.objects.filter(
                user=user,
                status__in=[Subscription.Status.ACTIVE, Subscription.Status.TRIALING],
            ).exists()
            if has_sub:
                factor = Decimal(100 - self.subscriber_discount_percent) / Decimal(100)
                price = (price * factor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return price


class StorySubmission(models.Model):
    """A paid submission of a story to be reviewed and published as a featured blog post."""

    class Status(models.TextChoices):
        PENDING_PAYMENT = 'pending_payment', 'Pending payment'
        IN_REVIEW = 'in_review', 'In review'
        PUBLISHED = 'published', 'Published'
        REJECTED = 'rejected', 'Rejected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=12, unique=True, editable=False)
    package = models.ForeignKey(StoryPackage, on_delete=models.PROTECT, related_name='submissions')
    company = models.ForeignKey('profiles.CompanyProfile', on_delete=models.CASCADE, related_name='story_submissions')
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='story_submissions')
    kind = models.CharField(max_length=20, choices=StoryPackage.Kind.choices)

    title = models.CharField(max_length=200)
    body = models.TextField(help_text='The story text (plain text; paragraphs become blog paragraphs).')
    cover_image = models.ImageField(upload_to='promotions/', null=True, blank=True)
    contact_email = models.EmailField()

    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING_PAYMENT)
    admin_note = models.CharField(max_length=400, blank=True,
        help_text='Feedback shown to the business (e.g. why it was rejected).')

    published_post = models.ForeignKey('blog.BlogPost', on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='promotion')
    featured_until = models.DateTimeField(null=True, blank=True)

    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='reviewed_stories')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    stripe_session_id = models.CharField(max_length=200, blank=True)
    stripe_payment_intent = models.CharField(max_length=200, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['submitted_by', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'{self.reference} · {self.title} ({self.status})'

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._gen_reference()
        super().save(*args, **kwargs)

    @staticmethod
    def _gen_reference():
        while True:
            ref = 'ST' + uuid.uuid4().hex[:8].upper()
            if not StorySubmission.objects.filter(reference=ref).exists():
                return ref

    def _body_html(self):
        paras = [p.strip() for p in re.split(r'\n\s*\n', self.body) if p.strip()]
        return ''.join(f'<p>{p}</p>' for p in paras) or f'<p>{self.body}</p>'

    def publish(self, reviewer=None):
        """Create (or refresh) a featured blog post from this submission and mark it published."""
        from apps.blog.models import BlogPost, BlogCategory
        category = BlogCategory.objects.filter(slug=KIND_CATEGORY.get(self.kind, 'success-stories')).first()
        now = timezone.now()

        post = self.published_post or BlogPost()
        post.title = self.title
        post.author = self.submitted_by
        post.category = category
        post.content = self._body_html()
        post.excerpt = post.excerpt or (re.sub(r'<[^>]+>', '', self._body_html())[:250].strip())
        if self.cover_image:
            post.cover_image = self.cover_image
        post.tags = self.company.company_name
        post.status = BlogPost.Status.PUBLISHED
        post.is_featured = True
        if not post.published_at:
            post.published_at = now
        post.save()

        self.published_post = post
        self.status = self.Status.PUBLISHED
        self.featured_until = now + timedelta(days=self.package.duration_days)
        self.reviewed_by = reviewer
        self.reviewed_at = now
        self.admin_note = ''
        self.save()
        return post

    def reject(self, reviewer=None, note=''):
        self.status = self.Status.REJECTED
        self.admin_note = note
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save()
