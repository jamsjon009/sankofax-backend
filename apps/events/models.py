import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
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
    ticket_url = models.URLField(blank=True,
        help_text='External ticketing link. Leave blank to use on-platform RSVP instead.')
    ticket_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    # --- In-platform ticketing / RSVP (item #16) ---
    rsvp_enabled = models.BooleanField(default=False,
        help_text='Allow attendees to RSVP / reserve tickets on SankofaX.')
    capacity = models.PositiveIntegerField(null=True, blank=True,
        help_text='Maximum confirmed attendees. Leave blank for unlimited.')
    allow_waitlist = models.BooleanField(default=True,
        help_text='When full, place further sign-ups on a waitlist.')
    registration_deadline = models.DateTimeField(null=True, blank=True,
        help_text='Last moment attendees can register. Defaults to the event start time.')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_datetime']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Event, self.title)
        super().save(*args, **kwargs)

    # --- RSVP helpers -----------------------------------------------------
    @property
    def confirmed_count(self):
        """Number of confirmed seats (sums ticket quantity)."""
        return (self.registrations
                .filter(status=EventRegistration.Status.CONFIRMED)
                .aggregate(n=models.Sum('quantity'))['n'] or 0)

    @property
    def waitlist_count(self):
        return (self.registrations
                .filter(status=EventRegistration.Status.WAITLISTED)
                .aggregate(n=models.Sum('quantity'))['n'] or 0)

    @property
    def spots_left(self):
        """Remaining confirmed capacity, or None when capacity is unlimited."""
        if self.capacity is None:
            return None
        return max(self.capacity - self.confirmed_count, 0)

    @property
    def is_full(self):
        return self.capacity is not None and self.confirmed_count >= self.capacity

    @property
    def registration_closes_at(self):
        return self.registration_deadline or self.start_datetime

    @property
    def registration_open(self):
        """Whether new RSVPs are currently accepted."""
        if not self.rsvp_enabled or self.status != self.Status.PUBLISHED:
            return False
        return timezone.now() <= self.registration_closes_at


class EventRegistration(models.Model):
    """An attendee's RSVP / ticket reservation for an on-platform event."""

    class Status(models.TextChoices):
        CONFIRMED = 'confirmed', 'Confirmed'
        WAITLISTED = 'waitlisted', 'Waitlisted'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    attendee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='event_registrations')
    # Snapshot of the attendee's details at sign-up (survives profile edits).
    name = models.CharField(max_length=150)
    email = models.EmailField()
    quantity = models.PositiveSmallIntegerField(default=1,
        help_text='Number of seats / tickets reserved.')
    note = models.CharField(max_length=300, blank=True,
        help_text='Optional message to the organizer (e.g. accessibility needs).')
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.CONFIRMED)
    ticket_code = models.CharField(max_length=12, unique=True, editable=False)
    checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        constraints = [
            # One active registration per user per event (cancelled rows may repeat).
            models.UniqueConstraint(
                fields=['event', 'attendee'],
                condition=~models.Q(status='cancelled'),
                name='uniq_active_registration_per_event_attendee',
            ),
        ]
        indexes = [
            models.Index(fields=['event', 'status']),
            models.Index(fields=['attendee', 'status']),
        ]

    def __str__(self):
        return f'{self.name} · {self.event.title} ({self.status})'

    def save(self, *args, **kwargs):
        if not self.ticket_code:
            self.ticket_code = self._generate_code()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_code():
        while True:
            code = 'SX' + uuid.uuid4().hex[:8].upper()
            if not EventRegistration.objects.filter(ticket_code=code).exists():
                return code
