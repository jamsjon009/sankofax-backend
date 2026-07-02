from rest_framework import serializers
from .models import Category, Amenity, Listing, ListingImage


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'description', 'listing_type', 'subcategories']

    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            return CategorySerializer(obj.subcategories.all(), many=True).data
        return []


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'slug', 'icon']


class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ['id', 'image', 'caption', 'order']


class ListingCardSerializer(serializers.ModelSerializer):
    """Compact serializer for list/card views."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    company_verified = serializers.BooleanField(source='company.is_verified', read_only=True)
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            'id', 'slug', 'title', 'short_description', 'city', 'country',
            'avg_rating', 'review_count', 'price_range', 'featured',
            'category_name', 'category_slug', 'company_name', 'company_verified',
            'cover_image',
        ]

    def get_cover_image(self, obj):
        first = obj.gallery_images.first()
        if first:
            request = self.context.get('request')
            return request.build_absolute_uri(first.image.url) if request else first.image.url
        return None


class ListingDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    gallery_images = ListingImageSerializer(many=True, read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    company_slug = serializers.CharField(source='company.slug', read_only=True)
    company_verified = serializers.BooleanField(source='company.is_verified', read_only=True)
    company_logo = serializers.ImageField(source='company.logo', read_only=True)

    class Meta:
        model = Listing
        fields = [
            'id', 'slug', 'title', 'short_description', 'full_description',
            'listing_status', 'featured', 'address_line', 'city', 'state',
            'country', 'postal_code', 'latitude', 'longitude',
            'phone', 'email', 'website', 'whatsapp', 'price_range',
            'opening_hours', 'avg_rating', 'review_count', 'view_count',
            'category', 'amenities', 'gallery_images',
            'company_name', 'company_slug', 'company_verified', 'company_logo',
            'created_at', 'published_at',
        ]


class ListingCreateUpdateSerializer(serializers.ModelSerializer):
    amenity_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Amenity.objects.all(), source='amenities', required=False
    )

    class Meta:
        model = Listing
        fields = [
            'company', 'category', 'secondary_categories', 'title', 'short_description',
            'full_description', 'address_line', 'city', 'state', 'country', 'postal_code',
            'latitude', 'longitude', 'phone', 'email', 'website', 'whatsapp',
            'price_range', 'opening_hours', 'amenity_ids',
        ]

    def create(self, validated_data):
        validated_data['listing_status'] = Listing.Status.PENDING
        return super().create(validated_data)
