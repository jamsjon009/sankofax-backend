from rest_framework import serializers
from .models import Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'order']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'company', 'company_name', 'category', 'name', 'slug',
            'description', 'price', 'currency', 'stock_status',
            'external_purchase_url', 'is_active', 'images', 'created_at',
        ]
        read_only_fields = ['id', 'slug', 'company_name', 'created_at']
