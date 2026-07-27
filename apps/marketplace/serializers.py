from rest_framework import serializers
from .models import Product, ProductImage, Service, Order, OrderItem, ServiceBooking


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'order']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    company_slug = serializers.CharField(source='company.slug', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'company', 'company_name', 'company_slug', 'category', 'name', 'slug',
            'description', 'price', 'currency', 'stock_status',
            'external_purchase_url', 'is_active', 'images', 'created_at',
        ]
        read_only_fields = ['id', 'slug', 'company_name', 'company_slug', 'created_at']


class ServiceSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    company_slug = serializers.CharField(source='company.slug', read_only=True)

    class Meta:
        model = Service
        fields = [
            'id', 'company', 'company_name', 'company_slug', 'category', 'name', 'slug',
            'description', 'price', 'currency', 'duration_minutes', 'is_virtual',
            'location', 'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'slug', 'company_name', 'company_slug', 'created_at']


# --- Orders -----------------------------------------------------------------

class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True, default=None)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_slug', 'name', 'unit_price', 'quantity', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    buyer_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'company', 'company_name', 'buyer_name', 'status',
            'currency', 'total', 'contact_name', 'contact_email', 'shipping_address',
            'note', 'items', 'paid_at', 'created_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_buyer_name(self, obj):
        return obj.contact_name or (obj.buyer.get_full_name() if obj.buyer else '')


class CheckoutItemInput(serializers.Serializer):
    product = serializers.SlugField()  # product slug
    quantity = serializers.IntegerField(min_value=1, max_value=99, default=1)


class CheckoutSerializer(serializers.Serializer):
    """Input for POST /marketplace/checkout/."""
    items = CheckoutItemInput(many=True)
    contact_name = serializers.CharField(max_length=150)
    contact_email = serializers.EmailField()
    shipping_address = serializers.CharField(required=False, allow_blank=True, default='')
    note = serializers.CharField(max_length=300, required=False, allow_blank=True, default='')

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('Your cart is empty.')
        return value


# --- Service bookings -------------------------------------------------------

class ServiceBookingSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    service_slug = serializers.CharField(source='service.slug', read_only=True, default=None)
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = ServiceBooking
        fields = [
            'id', 'booking_number', 'service', 'service_slug', 'service_name', 'company',
            'company_name', 'customer_name', 'scheduled_for', 'status', 'currency', 'total',
            'contact_name', 'contact_email', 'note', 'paid_at', 'created_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_customer_name(self, obj):
        return obj.contact_name or (obj.customer.get_full_name() if obj.customer else '')


class BookingCreateSerializer(serializers.Serializer):
    """Input for POST /marketplace/bookings/."""
    service = serializers.SlugField()  # service slug
    scheduled_for = serializers.DateTimeField()
    contact_name = serializers.CharField(max_length=150)
    contact_email = serializers.EmailField()
    note = serializers.CharField(max_length=300, required=False, allow_blank=True, default='')
