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


# ---------------------------------------------------------------------------
# In-platform checkout & service booking (item #17)
# ---------------------------------------------------------------------------

def _short_code(prefix, model_class, field):
    while True:
        code = prefix + uuid.uuid4().hex[:8].upper()
        if not model_class.objects.filter(**{field: code}).exists():
            return code


class Service(models.Model):
    """A bookable service offered by a business (e.g. a consultation, a session)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('profiles.CompanyProfile', on_delete=models.CASCADE,
                                related_name='bookable_services')
    category = models.ForeignKey('directory.Category', on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0,
        help_text='0 = free booking request (customer pays nothing online).')
    currency = models.CharField(max_length=3, default='USD')
    duration_minutes = models.PositiveIntegerField(default=60)
    is_virtual = models.BooleanField(default=False)
    location = models.CharField(max_length=200, blank=True, help_text='City or venue for in-person services.')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Service, self.name)
        super().save(*args, **kwargs)


class Order(models.Model):
    """A product purchase placed on-platform (paid via Stripe Checkout)."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending payment'
        PAID = 'paid', 'Paid'
        FULFILLED = 'fulfilled', 'Fulfilled'
        CANCELLED = 'cancelled', 'Cancelled'
        REFUNDED = 'refunded', 'Refunded'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=12, unique=True, editable=False)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    # Every order is fulfilled by a single business (marketplace is per-seller).
    company = models.ForeignKey('profiles.CompanyProfile', on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    currency = models.CharField(max_length=3, default='USD')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    contact_name = models.CharField(max_length=150)
    contact_email = models.EmailField()
    shipping_address = models.TextField(blank=True)
    note = models.CharField(max_length=300, blank=True)
    stripe_session_id = models.CharField(max_length=200, blank=True)
    stripe_payment_intent = models.CharField(max_length=200, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['buyer', '-created_at']),
            models.Index(fields=['company', 'status']),
        ]

    def __str__(self):
        return f'Order {self.order_number} ({self.status})'

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = _short_code('SX', Order, 'order_number')
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    name = models.CharField(max_length=200)  # snapshot
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} × {self.name}'

    @property
    def subtotal(self):
        return self.unit_price * self.quantity


class ServiceBooking(models.Model):
    """A customer's booking of a service. Paid services confirm on payment;
    free services become a request the business confirms/declines."""

    class Status(models.TextChoices):
        PENDING_PAYMENT = 'pending_payment', 'Pending payment'
        PENDING = 'pending', 'Pending confirmation'
        CONFIRMED = 'confirmed', 'Confirmed'
        COMPLETED = 'completed', 'Completed'
        DECLINED = 'declined', 'Declined'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking_number = models.CharField(max_length=12, unique=True, editable=False)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, related_name='bookings')
    company = models.ForeignKey('profiles.CompanyProfile', on_delete=models.CASCADE, related_name='bookings')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_bookings')
    service_name = models.CharField(max_length=200)  # snapshot
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    currency = models.CharField(max_length=3, default='USD')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    contact_name = models.CharField(max_length=150)
    contact_email = models.EmailField()
    note = models.CharField(max_length=300, blank=True)
    stripe_session_id = models.CharField(max_length=200, blank=True)
    stripe_payment_intent = models.CharField(max_length=200, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', '-created_at']),
            models.Index(fields=['company', 'status']),
        ]

    def __str__(self):
        return f'Booking {self.booking_number} ({self.status})'

    def save(self, *args, **kwargs):
        if not self.booking_number:
            self.booking_number = _short_code('BK', ServiceBooking, 'booking_number')
        super().save(*args, **kwargs)
