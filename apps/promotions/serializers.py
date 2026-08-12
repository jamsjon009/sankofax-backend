from rest_framework import serializers
from apps.profiles.models import CompanyProfile
from .models import StoryPackage, StorySubmission


class StoryPackageSerializer(serializers.ModelSerializer):
    your_price = serializers.SerializerMethodField()
    kind_label = serializers.CharField(source='get_kind_display', read_only=True)

    class Meta:
        model = StoryPackage
        fields = [
            'id', 'name', 'slug', 'kind', 'kind_label', 'price', 'your_price', 'currency',
            'duration_days', 'subscriber_discount_percent', 'description', 'features_list',
        ]

    def get_your_price(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        return str(obj.price_for(user))


class StorySubmissionSerializer(serializers.ModelSerializer):
    package_name = serializers.CharField(source='package.name', read_only=True)
    kind_label = serializers.CharField(source='get_kind_display', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    post_slug = serializers.CharField(source='published_post.slug', read_only=True, default=None)

    class Meta:
        model = StorySubmission
        fields = [
            'id', 'reference', 'package', 'package_name', 'kind', 'kind_label',
            'company', 'company_name', 'title', 'body', 'cover_image', 'contact_email',
            'amount', 'currency', 'status', 'admin_note', 'post_slug', 'featured_until',
            'paid_at', 'created_at', 'updated_at',
        ]
        read_only_fields = fields


class StorySubmissionCreateSerializer(serializers.Serializer):
    """Multipart create: package slug, company slug, story content, optional cover."""
    package = serializers.SlugRelatedField(
        slug_field='slug', queryset=StoryPackage.objects.filter(is_active=True))
    company = serializers.SlugRelatedField(
        slug_field='slug', queryset=CompanyProfile.objects.all())
    title = serializers.CharField(max_length=200)
    body = serializers.CharField()
    contact_email = serializers.EmailField()
    cover_image = serializers.ImageField(required=False, allow_null=True)

    def validate_title(self, value):
        if len(value.strip()) < 8:
            raise serializers.ValidationError('Please use a more descriptive title (at least 8 characters).')
        return value.strip()

    def validate_body(self, value):
        if len(value.strip()) < 120:
            raise serializers.ValidationError('Your story is too short — please write at least a couple of paragraphs.')
        return value

    def validate_company(self, company):
        request = self.context['request']
        if company.owner_id != request.user.id and not request.user.is_staff:
            raise serializers.ValidationError('You can only promote a business you own.')
        return company
