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


class Product(models.Model):
    class StockStatus(models.TextChoices):
        IN_STOCK = 'in_stock', 'In Stock'
        OUT_OF_STOCK = 'out_of_stock', 'Out of Stock'
        MADE_TO_ORDER = 'made_to_order', 'Made to Order'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('profiles.CompanyProfile', on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey('directory.Category', on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    stock_status = models.CharField(max_length=20, choices=StockStatus.choices, default=StockStatus.IN_STOCK)
    external_purchase_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Product, self.name)
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
