from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Product, ProductImage, Service, Order, OrderItem, ServiceBooking


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ['name', 'company', 'price', 'currency', 'stock_status', 'is_active']
    list_per_page = 10
    list_filter = ['stock_status', 'is_active', 'category']
    search_fields = ['name', 'company__company_name']
    readonly_fields = ['slug', 'created_at']
    inlines = [ProductImageInline]


@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    list_display = ['name', 'company', 'price', 'currency', 'duration_minutes', 'is_virtual', 'is_active']
    list_per_page = 10
    list_filter = ['is_active', 'is_virtual', 'category']
    search_fields = ['name', 'company__company_name']
    readonly_fields = ['slug', 'created_at']


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'name', 'unit_price', 'quantity']
    can_delete = False


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ['order_number', 'company', 'contact_name', 'total', 'currency', 'status', 'created_at']
    list_per_page = 25
    list_filter = ['status', 'currency']
    search_fields = ['order_number', 'contact_name', 'contact_email', 'company__company_name']
    readonly_fields = ['order_number', 'buyer', 'company', 'total', 'currency',
                       'stripe_session_id', 'stripe_payment_intent', 'paid_at', 'created_at', 'updated_at']
    inlines = [OrderItemInline]


@admin.register(ServiceBooking)
class ServiceBookingAdmin(ModelAdmin):
    list_display = ['booking_number', 'service_name', 'company', 'contact_name',
                    'scheduled_for', 'total', 'status', 'created_at']
    list_per_page = 25
    list_filter = ['status', 'currency']
    search_fields = ['booking_number', 'service_name', 'contact_name', 'contact_email', 'company__company_name']
    readonly_fields = ['booking_number', 'customer', 'company', 'service', 'service_name', 'total', 'currency',
                       'stripe_session_id', 'stripe_payment_intent', 'paid_at', 'created_at', 'updated_at']
