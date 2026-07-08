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


class CompanyProfile(models.Model):
    class Size(models.TextChoices):
        SOLO = 'solo', 'Solo'
        SMALL = '1-10', '1–10 employees'
        MEDIUM = '11-50', '11–50 employees'
        LARGE = '51+', '51+ employees'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='companies')
    company_name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='covers/', null=True, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    company_size = models.CharField(max_length=10, choices=Size.choices, default=Size.SOLO)
    description = CKEditor5Field(config_name='minimal', blank=True)
    website = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_documents = models.FileField(upload_to='verifications/', null=True, blank=True)
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
