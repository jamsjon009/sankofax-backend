import uuid
from django.db import models
from django.conf import settings


class Connection(models.Model):
    """A 'Connect' request or a 'Collaborate' inquiry sent from one user to a business owner."""

    class Kind(models.TextChoices):
        CONNECT = 'connect', 'Connect'
        COLLABORATE = 'collaborate', 'Collaborate'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        DECLINED = 'declined', 'Declined'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='sent_connections')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='received_connections')
    listing = models.ForeignKey('directory.Listing', on_delete=models.CASCADE,
                                null=True, blank=True, related_name='connections')
    kind = models.CharField(max_length=12, choices=Kind.choices, default=Kind.CONNECT)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    is_read = models.BooleanField(default=False, help_text='Has the recipient seen this?')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['sender']),
        ]

    def __str__(self):
        return f'{self.sender_id} -> {self.recipient_id} ({self.kind}/{self.status})'
