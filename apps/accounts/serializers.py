from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


GLOBAL_NORTH_COUNTRIES = {
    'US', 'CA', 'GB', 'AU', 'NZ', 'DE', 'FR', 'IT', 'ES', 'PT', 'NL', 'BE',
    'CH', 'AT', 'SE', 'NO', 'DK', 'FI', 'IE', 'LU', 'IS', 'LI', 'MC', 'SM',
    'MT', 'CY', 'EE', 'LV', 'LT', 'SI', 'SK', 'CZ', 'PL', 'HU', 'HR', 'BG',
    'RO', 'GR', 'JP', 'SG', 'KR', 'IL', 'AE', 'QA', 'KW', 'BH', 'SA',
}


def country_to_region(country_code):
    if country_code and country_code.upper() in GLOBAL_NORTH_COUNTRIES:
        return User.Region.GLOBAL_NORTH
    return User.Region.GLOBAL_SOUTH


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)
    country = serializers.CharField(max_length=2, required=False, allow_blank=True)
    account_type = serializers.ChoiceField(
        choices=['visitor', 'business'],
        required=False,
        write_only=True,
        default='visitor',
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'phone_number', 'region', 'country', 'account_type']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        account_type = validated_data.pop('account_type', 'visitor')
        country = validated_data.get('country', '')

        # Auto-derive region from country if not explicitly provided
        if not validated_data.get('region') and country:
            validated_data['region'] = country_to_region(country)

        # Set role based on account type
        if account_type == 'business':
            validated_data['role'] = User.Role.BUSINESS_OWNER
        else:
            validated_data['role'] = User.Role.VISITOR

        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(email=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials.')
        if not user.is_active:
            raise serializers.ValidationError('Account is disabled.')
        if not user.is_verified:
            raise serializers.ValidationError(
                'Please verify your email address before signing in. Check your inbox for the verification link.'
            )
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone_number', 'role', 'is_verified',
            'region', 'country', 'avatar', 'date_joined',
        ]
        read_only_fields = ['id', 'role', 'is_verified', 'date_joined']


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(min_length=8, write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs