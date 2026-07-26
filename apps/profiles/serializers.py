from rest_framework import serializers
from .models import UserProfile, CompanyProfile, IdentityBadge


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['bio', 'country', 'city', 'date_of_birth', 'social_links', 'preferences']


class IdentityBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentityBadge
        fields = ['id', 'name', 'slug', 'icon', 'color', 'description']


class CompanyProfileSerializer(serializers.ModelSerializer):
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    badges = IdentityBadgeSerializer(many=True, read_only=True)
    services_list = serializers.ListField(child=serializers.CharField(), read_only=True)
    social_links = serializers.DictField(read_only=True)

    class Meta:
        model = CompanyProfile
        fields = [
            'id', 'owner_email', 'company_name', 'slug', 'logo', 'cover_image',
            'founded_year', 'company_size', 'description', 'founder_story', 'website',
            'contact_email', 'contact_phone', 'services', 'services_list',
            'instagram_url', 'facebook_url', 'twitter_url', 'linkedin_url',
            'youtube_url', 'tiktok_url', 'social_links',
            'is_verified', 'badges', 'created_at',
        ]
        read_only_fields = ['id', 'slug', 'is_verified', 'created_at', 'owner_email']


class CompanyProfileCreateSerializer(serializers.ModelSerializer):
    badges = serializers.PrimaryKeyRelatedField(
        many=True, queryset=IdentityBadge.objects.all(), required=False,
    )

    class Meta:
        model = CompanyProfile
        fields = [
            'company_name', 'logo', 'cover_image', 'founded_year', 'company_size',
            'description', 'founder_story', 'website', 'contact_email', 'contact_phone',
            'services', 'instagram_url', 'facebook_url', 'twitter_url', 'linkedin_url',
            'youtube_url', 'tiktok_url', 'verification_documents', 'badges',
        ]

    def create(self, validated_data):
        badges = validated_data.pop('badges', None)
        validated_data['owner'] = self.context['request'].user
        company = super().create(validated_data)
        if badges is not None:
            company.badges.set(badges)
        return company

    def update(self, instance, validated_data):
        badges = validated_data.pop('badges', None)
        company = super().update(instance, validated_data)
        if badges is not None:
            company.badges.set(badges)
        return company
