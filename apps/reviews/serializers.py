from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'listing', 'user_email', 'user_avatar', 'rating', 'title', 'body',
            'status', 'owner_reply', 'owner_reply_at', 'created_at',
        ]
        read_only_fields = ['id', 'user_email', 'user_avatar', 'status', 'owner_reply', 'owner_reply_at', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class OwnerReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['owner_reply']
