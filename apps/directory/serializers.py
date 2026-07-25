from rest_framework import serializers
from .models import Category, Amenity, Listing, ListingImage


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'description', 'listing_type', 'cover_image', 'subcategories']

    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            return CategorySerializer(obj.subcategories.all(), many=True, context=self.context).data
        return []

    def get_cover_image(self, obj):
        if not obj.cover_image:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.cover_image.url) if request else obj.cover_image.url


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'slug', 'icon']


class ListingImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ListingImage
        fields = ['id', 'image', 'caption', 'order']

    def get_image(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url


class ListingCardSerializer(serializers.ModelSerializer):
    """Compact serializer for list/card views."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    company_verified = serializers.BooleanField(source='company.is_verified', read_only=True)
    cover_image = serializers.SerializerMethodField()
    gallery_images = serializers.SerializerMethodField()
    badges = serializers.SerializerMethodField()
    business_type_display = serializers.CharField(source='get_business_type_display', read_only=True)

    class Meta:
        model = Listing
        fields = [
            'id', 'slug', 'title', 'short_description', 'city', 'country',
            'avg_rating', 'review_count', 'price_range', 'featured',
            'business_type', 'business_type_display',
            'category_name', 'category_slug', 'company_name', 'company_verified',
            'cover_image', 'gallery_images', 'badges',
        ]

    def get_badges(self, obj):
        if not obj.company:
            return []
        from apps.profiles.serializers import IdentityBadgeSerializer
        return IdentityBadgeSerializer(obj.company.badges.all(), many=True).data

    def get_cover_image(self, obj):
        first = obj.gallery_images.first()
        if first:
            request = self.context.get('request')
            return request.build_absolute_uri(first.image.url) if request else first.image.url
        return None

    def get_gallery_images(self, obj):
        request = self.context.get('request')
        return [
            request.build_absolute_uri(img.image.url) if request else img.image.url
            for img in obj.gallery_images.all()
        ]


class ListingDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    gallery_images = ListingImageSerializer(many=True, read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    company_slug = serializers.CharField(source='company.slug', read_only=True)
    company_verified = serializers.BooleanField(source='company.is_verified', read_only=True)
    company_founder_story = serializers.CharField(source='company.founder_story', read_only=True, default='')
    company_logo = serializers.SerializerMethodField()
    badges = serializers.SerializerMethodField()
    business_type_display = serializers.CharField(source='get_business_type_display', read_only=True)

    def get_company_logo(self, obj):
        if obj.company and obj.company.logo:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.company.logo.url) if request else obj.company.logo.url
        return None

    def get_badges(self, obj):
        if not obj.company:
            return []
        from apps.profiles.serializers import IdentityBadgeSerializer
        return IdentityBadgeSerializer(obj.company.badges.all(), many=True).data

    class Meta:
        model = Listing
        fields = [
            'id', 'slug', 'title', 'short_description', 'full_description',
            'listing_status', 'featured', 'address_line', 'city', 'state',
            'country', 'postal_code', 'latitude', 'longitude',
            'phone', 'email', 'website', 'whatsapp', 'price_range',
            'business_type', 'business_type_display',
            'opening_hours', 'avg_rating', 'review_count', 'view_count',
            'category', 'amenities', 'gallery_images', 'badges',
            'company_name', 'company_slug', 'company_verified', 'company_founder_story', 'company_logo',
            'meta_title', 'meta_description', 'og_image',
            'created_at', 'published_at',
        ]


class ListingCreateUpdateSerializer(serializers.ModelSerializer):
    amenity_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Amenity.objects.all(), source='amenities', required=False
    )

    class Meta:
        model = Listing
        fields = [
            'company', 'category', 'secondary_categories', 'business_type', 'title', 'short_description',
            'full_description', 'address_line', 'city', 'state', 'country', 'postal_code',
            'latitude', 'longitude', 'phone', 'email', 'website', 'whatsapp',
            'price_range', 'opening_hours', 'amenity_ids',
        ]

    def create(self, validated_data):
        validated_data['listing_status'] = Listing.Status.PENDING
        return super().create(validated_data)
