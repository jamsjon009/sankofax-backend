import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify


def unique_slug(model_class, value, slug_field='slug'):
    slug = slugify(value) or 'thread'
    base = slug
    n = 1
    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f'{base}-{n}'
        n += 1
    return slug


class ForumCategory(models.Model):
    """A discussion board, e.g. General, Business Networking, Investor Matchmaking."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=120)
    description = models.CharField(max_length=250, blank=True)
    icon = models.CharField(max_length=40, blank=True,
        help_text='Optional emoji or lucide icon name shown with the board.')
    order = models.PositiveIntegerField(default=0, help_text='Lower = shown first')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Forum Category'
        verbose_name_plural = 'Forum Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(ForumCategory, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def thread_count(self):
        return self.threads.count()


class Thread(models.Model):
    """A discussion topic started by a member."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        ForumCategory, on_delete=models.CASCADE, related_name='threads')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='forum_threads')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    body = models.TextField(help_text='The opening post (plain text).')
    is_pinned = models.BooleanField(default=False, help_text='Pinned threads sort to the top.')
    is_locked = models.BooleanField(default=False, help_text='Locked threads cannot receive new replies.')
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity_at = models.DateTimeField(default=timezone.now,
        help_text='Updated whenever a reply is added — used for ordering.')

    class Meta:
        ordering = ['-is_pinned', '-last_activity_at']
        indexes = [
            models.Index(fields=['-last_activity_at']),
            models.Index(fields=['category', '-last_activity_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Thread, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def reply_count(self):
        return self.replies.count()


class Reply(models.Model):
    """A reply to a thread."""
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='forum_replies')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Reply'
        verbose_name_plural = 'Replies'

    def __str__(self):
        return f'Reply by {self.author} on {self.thread}'
