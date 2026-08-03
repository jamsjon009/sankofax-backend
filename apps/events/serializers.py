from rest_framework import serializers
from .models import Event, EventRegistration


class EventSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source='organizer.company_name', read_only=True)

    # --- RSVP / ticketing (item #16) ---
    confirmed_count = serializers.IntegerField(read_only=True)
    spots_left = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    registration_open = serializers.BooleanField(read_only=True)
    registration_closes_at = serializers.DateTimeField(read_only=True)
    my_registration = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'organizer', 'organizer_name', 'category', 'title', 'slug',
            'description', 'city', 'country', 'venue_name', 'latitude', 'longitude',
            'start_datetime', 'end_datetime', 'timezone', 'is_virtual', 'virtual_link',
            'cover_image', 'ticket_url', 'ticket_price', 'currency', 'status', 'created_at',
            # RSVP
            'rsvp_enabled', 'capacity', 'allow_waitlist', 'registration_deadline',
            'confirmed_count', 'spots_left', 'is_full', 'registration_open',
            'registration_closes_at', 'my_registration',
        ]
        read_only_fields = ['id', 'slug', 'organizer_name', 'created_at']

    def create(self, validated_data):
        instance = super().create(validated_data)
        self._maybe_geocode(instance)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        self._maybe_geocode(instance)
        return instance

    def _maybe_geocode(self, instance):
        """Auto-fill coordinates from the venue/city when the client didn't
        supply them. Explicit lat/long always wins."""
        data = self.initial_data
        if data.get('latitude') in (None, '') and data.get('longitude') in (None, ''):
            from apps.core.geocoding import geocode_event
            geocode_event(instance, force=True)

    def get_my_registration(self, obj):
        """The requesting user's active registration for this event, if any."""
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not (user and user.is_authenticated):
            return None
        reg = next(
            (r for r in obj.registrations.all()
             if r.attendee_id == user.id and r.status != EventRegistration.Status.CANCELLED),
            None,
        )
        return EventRegistrationSerializer(reg).data if reg else None


class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = [
            'id', 'name', 'email', 'quantity', 'note', 'status', 'ticket_code',
            'checked_in', 'checked_in_at', 'created_at',
        ]
        read_only_fields = fields


class EventRegistrationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = ['quantity', 'note']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('Reserve at least one ticket.')
        if value > 10:
            raise serializers.ValidationError('You can reserve at most 10 tickets at once.')
        return value


class AttendeeSerializer(serializers.ModelSerializer):
    """Organizer-facing view of a registration (includes attendee contact)."""

    class Meta:
        model = EventRegistration
        fields = [
            'id', 'name', 'email', 'quantity', 'note', 'status', 'ticket_code',
            'checked_in', 'checked_in_at', 'created_at',
        ]
        read_only_fields = fields


class MyTicketSerializer(EventRegistrationSerializer):
    """A registration bundled with the essentials of its event, for the attendee's tickets list."""
    event = serializers.SerializerMethodField()

    class Meta(EventRegistrationSerializer.Meta):
        fields = EventRegistrationSerializer.Meta.fields + ['event']
        read_only_fields = fields

    def get_event(self, obj):
        e = obj.event
        return {
            'id': str(e.id),
            'title': e.title,
            'slug': e.slug,
            'city': e.city,
            'country': e.country,
            'venue_name': e.venue_name,
            'is_virtual': e.is_virtual,
            'start_datetime': e.start_datetime,
            'end_datetime': e.end_datetime,
            'cover_image': e.cover_image.url if e.cover_image else None,
            'status': e.status,
        }
