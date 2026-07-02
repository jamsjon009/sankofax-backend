from rest_framework import serializers
from .models import UserProfile, CompanyProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['bio', 'country', 'city', 'date_of_birth', 'social_links', 'preferences']


class CompanyProfileSerializer(serializers.ModelSerializer):
    owner_email = serializers.CharField(source='owner.email', read_only=True)

    class Meta:
        model = CompanyProfile
        fields = [
            'id', 'owner_email', 'company_name', 'slug', 'logo', 'cover_image',
            'founded_year', 'company_size', 'description', 'website',
            'contact_email', 'contact_phone', 'is_verified', 'created_at',
        ]
        read_only_fields = ['id', 'slug', 'is_verified', 'created_at', 'owner_email']


class CompanyProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = [
            'company_name', 'logo', 'cover_image', 'founded_year', 'company_size',
            'description', 'website', 'contact_email', 'contact_phone', 'verification_documents',
        ]

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)
