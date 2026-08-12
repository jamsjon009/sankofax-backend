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


class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Blog Category'
        verbose_name_plural = 'Blog Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(BlogCategory, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def post_count(self):
        return self.posts.filter(status=BlogPost.Status.PUBLISHED).count()


class BlogPost(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        ARCHIVED = 'archived', 'Archived'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blog_posts',
    )
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
    )
    tags = models.CharField(max_length=300, blank=True, help_text='Comma-separated tags')
    excerpt = models.TextField(max_length=300, blank=True, help_text='Short summary shown on listing page')
    content = CKEditor5Field(config_name='default', help_text='Rich text content')
    cover_image = models.ImageField(upload_to='blog/covers/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    is_featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    read_time_minutes = models.PositiveIntegerField(default=5)

    # SEO
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    og_image = models.ImageField(upload_to='blog/og/', null=True, blank=True)

    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(BlogPost, self.title)
        if not self.excerpt and self.content:
            import re
            text = re.sub(r'<[^>]+>', '', self.content)
            self.excerpt = text[:250].strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def tags_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    @property
    def author_name(self):
        if self.author:
            return self.author.email.split('@')[0]
        return 'SankofaX'