from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Product, ProductImage


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ['name', 'company', 'price', 'currency', 'stock_status', 'is_active']
    list_filter = ['stock_status', 'is_active', 'category']
    search_fields = ['name', 'company__company_name']
    readonly_fields = ['slug', 'created_at']
    inlines = [ProductImageInline]
