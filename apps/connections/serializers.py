from rest_framework import serializers
from apps.directory.models import Listing
from .models import Connection


def _display_name(user):
    full = user.get_full_name() if hasattr(user, 'get_full_name') else ''
    return (full or '').strip() or user.email.split('@')[0]


class ConnectionSerializer(serializers.ModelSerializer):
    """Read serializer for inbox / sent lists."""
    sender_name = serializers.SerializerMethodField()
    sender_email = serializers.CharField(source='sender.email', read_only=True)
    recipient_name = serializers.SerializerMethodField()
    listing_title = serializers.CharField(source='listing.title', read_only=True, default=None)
    listing_slug = serializers.CharField(source='listing.slug', read_only=True, default=None)
    company_name = serializers.CharField(source='listing.company.company_name', read_only=True, default=None)

    class Meta:
        model = Connection
        fields = [
            'id', 'kind', 'subject', 'message', 'status', 'is_read',
            'sender_name', 'sender_email', 'recipient_name',
            'listing_title', 'listing_slug', 'company_name',
            'created_at',
        ]

    def get_sender_name(self, obj):
        return _display_name(obj.sender)

    def get_recipient_name(self, obj):
        return _display_name(obj.recipient)


class ConnectionCreateSerializer(serializers.ModelSerializer):
    listing = serializers.SlugRelatedField(slug_field='slug', queryset=Listing.objects.all())

    class Meta:
        model = Connection
        fields = ['id', 'listing', 'kind', 'subject', 'message']
        read_only_fields = ['id']

    def validate(self, attrs):
        request = self.context['request']
        listing = attrs['listing']
        owner = listing.company.owner if listing.company else None

        if owner is None:
            raise serializers.ValidationError('This listing has no owner to contact.')
        if owner == request.user:
            raise serializers.ValidationError("You can't send a request to your own business.")
        if attrs.get('kind') == Connection.Kind.COLLABORATE and not attrs.get('message', '').strip():
            raise serializers.ValidationError({'message': 'A message is required to collaborate.'})

        # Prevent duplicate pending requests of the same kind to the same listing.
        exists = Connection.objects.filter(
            sender=request.user, listing=listing,
            kind=attrs.get('kind', Connection.Kind.CONNECT),
            status=Connection.Status.PENDING,
        ).exists()
        if exists:
            raise serializers.ValidationError('You already have a pending request for this business.')

        attrs['_recipient'] = owner
        return attrs

    def create(self, validated_data):
        recipient = validated_data.pop('_recipient')
        return Connection.objects.create(
            sender=self.context['request'].user,
            recipient=recipient,
            **validated_data,
        )
