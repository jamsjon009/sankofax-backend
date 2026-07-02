import uuid
from django.db import models
from django.utils.text import slugify


def unique_slug(model_class, value, slug_field='slug'):
    slug = slugify(value)
    base = slug
    n = 1
    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f'{base}-{n}'
        n += 1
    return slug


class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PENDING = 'pending_review', 'Pending Review'
        PUBLISHED = 'published', 'Published'
        PAST = 'past', 'Past'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organizer = models.ForeignKey('profiles.CompanyProfile', on_delete=models.CASCADE, related_name='events')
    category = models.ForeignKey('directory.Category', on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    description = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    venue_name = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    timezone = models.CharField(max_length=50, default='UTC')
    is_virtual = models.BooleanField(default=False)
    virtual_link = models.URLField(blank=True)
    cover_image = models.ImageField(upload_to='events/', null=True, blank=True)
    ticket_url = models.URLField(blank=True)
    ticket_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_datetime']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Event, self.title)
        super().save(*args, **kwargs)
