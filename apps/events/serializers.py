from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source='organizer.company_name', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'organizer', 'organizer_name', 'category', 'title', 'slug',
            'description', 'city', 'country', 'venue_name', 'latitude', 'longitude',
            'start_datetime', 'end_datetime', 'timezone', 'is_virtual', 'virtual_link',
            'cover_image', 'ticket_url', 'ticket_price', 'currency', 'status', 'created_at',
        ]
        read_only_fields = ['id', 'slug', 'organizer_name', 'created_at']
