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


class Category(models.Model):
    class ListingType(models.TextChoices):
        BUSINESS = 'business', 'Business'
        EVENT = 'event', 'Event'
        PRODUCT = 'product', 'Product'

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Lucide icon name, e.g. "utensils"')
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subcategories')
    listing_type = models.CharField(max_length=10, choices=ListingType.choices, default=ListingType.BUSINESS)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Category, self.name)
        super().save(*args, **kwargs)


class Amenity(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name_plural = 'Amenities'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Amenity, self.name)
        super().save(*args, **kwargs)


class Listing(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PENDING = 'pending_review', 'Pending Review'
        PUBLISHED = 'published', 'Published'
        REJECTED = 'rejected', 'Rejected'
        SUSPENDED = 'suspended', 'Suspended'

    class PriceRange(models.TextChoices):
        BUDGET = '$', 'Budget ($)'
        MID = '$$', 'Mid-range ($$)'
        UPSCALE = '$$$', 'Upscale ($$$)'
        LUXURY = '$$$$', 'Luxury ($$$$)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('profiles.CompanyProfile', on_delete=models.CASCADE, related_name='listings')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='listings')
    secondary_categories = models.ManyToManyField(Category, blank=True, related_name='secondary_listings')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    short_description = models.CharField(max_length=300)
    full_description = models.TextField()
    listing_status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    featured = models.BooleanField(default=False)
    featured_until = models.DateTimeField(null=True, blank=True)

    # Location
    address_line = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # Contact
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)

    price_range = models.CharField(max_length=4, choices=PriceRange.choices, blank=True)
    opening_hours = models.JSONField(default=dict, blank=True)
    amenities = models.ManyToManyField(Amenity, blank=True)

    # Denormalized stats
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)

    # Moderation
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='reviewed_listings'
    )
    rejection_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-featured', '-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Listing, self.title)
        super().save(*args, **kwargs)


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='listings/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'Image for {self.listing.title}'
