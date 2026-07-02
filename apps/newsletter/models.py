from django.db import models


class Subscriber(models.Model):
    class Source(models.TextChoices):
        HOMEPAGE = 'homepage', 'Homepage'
        LISTING = 'listing', 'Listing Page'
        FOOTER = 'footer', 'Footer'
        OTHER = 'other', 'Other'

    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    source = models.CharField(max_length=10, choices=Source.choices, default=Source.HOMEPAGE)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email
