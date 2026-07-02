from django.db import models


class SiteSetting(models.Model):
    site_name = models.CharField(max_length=100, default='SankofaX')
    logo = models.ImageField(upload_to='site/', null=True, blank=True)
    contact_email = models.EmailField(blank=True)
    footer_text = models.TextField(blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    google_analytics_id = models.CharField(max_length=30, blank=True)

    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question
