from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        FLAGGED = 'flagged', 'Flagged'
        REMOVED = 'removed', 'Removed'

    listing = models.ForeignKey('directory.Listing', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    body = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    owner_reply = models.TextField(blank=True)
    owner_reply_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['listing', 'user']

    def __str__(self):
        return f'{self.user.email} → {self.listing.title} ({self.rating}★)'
