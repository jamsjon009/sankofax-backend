from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from django_filters.rest_framework import DjangoFilterBackend
from .models import Event, EventRegistration
from .serializers import (
    EventSerializer, EventRegistrationSerializer, EventRegistrationCreateSerializer,
    AttendeeSerializer, MyTicketSerializer,
)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.filter(status=Event.Status.PUBLISHED).prefetch_related('registrations')
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'country', 'is_virtual', 'category']
    search_fields = ['title', 'description', 'city', 'venue_name']
    ordering_fields = ['start_datetime', 'created_at']
    lookup_field = 'slug'

    def get_permissions(self):
        public = ['list', 'retrieve']
        authed = ['register', 'my_tickets', 'attendees', 'check_in']
        if self.action in public:
            return [permissions.AllowAny()]
        if self.action in authed:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    # ------------------------------------------------------------------ RSVP
    @action(detail=True, methods=['post', 'delete'], url_path='register')
    def register(self, request, slug=None):
        """
        POST   /api/events/{slug}/register/  -> RSVP / reserve tickets (confirmed or waitlisted).
        DELETE /api/events/{slug}/register/  -> cancel my RSVP (promotes the waitlist).
        """
        event = self.get_object()
        if request.method == 'DELETE':
            return self._cancel(request, event)
        return self._register(request, event)

    def _register(self, request, event):
        if not event.rsvp_enabled:
            raise ValidationError('This event does not use on-platform registration.')
        if not event.registration_open:
            raise ValidationError('Registration for this event is closed.')

        payload = EventRegistrationCreateSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        quantity = payload.validated_data['quantity']
        note = payload.validated_data.get('note', '')

        with transaction.atomic():
            locked = Event.objects.select_for_update().get(pk=event.pk)
            existing = (EventRegistration.objects
                        .filter(event=locked, attendee=request.user)
                        .exclude(status=EventRegistration.Status.CANCELLED)
                        .first())
            if existing:
                raise ValidationError('You are already registered for this event.')

            if locked.capacity is None:
                reg_status = EventRegistration.Status.CONFIRMED
            elif locked.confirmed_count + quantity <= locked.capacity:
                reg_status = EventRegistration.Status.CONFIRMED
            elif locked.allow_waitlist:
                reg_status = EventRegistration.Status.WAITLISTED
            else:
                raise ValidationError('This event is sold out.')

            reg = EventRegistration.objects.create(
                event=locked,
                attendee=request.user,
                name=(request.user.get_full_name() or '').strip() or request.user.email.split('@')[0],
                email=request.user.email,
                quantity=quantity,
                note=note,
                status=reg_status,
            )
        return Response(EventRegistrationSerializer(reg).data, status=status.HTTP_201_CREATED)

    def _cancel(self, request, event):
        with transaction.atomic():
            locked = Event.objects.select_for_update().get(pk=event.pk)
            reg = (EventRegistration.objects
                   .filter(event=locked, attendee=request.user)
                   .exclude(status=EventRegistration.Status.CANCELLED)
                   .first())
            if not reg:
                raise NotFound('You are not registered for this event.')
            was_confirmed = reg.status == EventRegistration.Status.CONFIRMED
            reg.status = EventRegistration.Status.CANCELLED
            reg.save(update_fields=['status', 'updated_at'])
            if was_confirmed:
                self._promote_waitlist(locked)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _promote_waitlist(event):
        """Confirm the earliest waitlisted registrations that fit the freed capacity (FIFO)."""
        if event.capacity is None:
            return
        waitlisted = (EventRegistration.objects
                      .filter(event=event, status=EventRegistration.Status.WAITLISTED)
                      .order_by('created_at'))
        for reg in waitlisted:
            if event.confirmed_count + reg.quantity <= event.capacity:
                reg.status = EventRegistration.Status.CONFIRMED
                reg.save(update_fields=['status', 'updated_at'])

    @action(detail=False, methods=['get'], url_path='my-tickets')
    def my_tickets(self, request):
        """GET /api/events/my-tickets/ -> the current user's registrations (with event info)."""
        regs = (EventRegistration.objects
                .filter(attendee=request.user)
                .exclude(status=EventRegistration.Status.CANCELLED)
                .select_related('event')
                .order_by('event__start_datetime'))
        return Response(MyTicketSerializer(regs, many=True).data)

    # --------------------------------------------------------- Organizer view
    def _require_organizer(self, request, event):
        if not (request.user.is_staff or event.organizer.owner_id == request.user.id):
            raise PermissionDenied('Only the event organizer can manage attendees.')

    @action(detail=True, methods=['get'], url_path='attendees')
    def attendees(self, request, slug=None):
        """GET /api/events/{slug}/attendees/ -> organizer-only attendee list."""
        event = self.get_object()
        self._require_organizer(request, event)
        regs = (event.registrations
                .exclude(status=EventRegistration.Status.CANCELLED)
                .select_related('attendee')
                .order_by('status', 'created_at'))
        return Response({
            'event': event.title,
            'capacity': event.capacity,
            'confirmed_count': event.confirmed_count,
            'waitlist_count': event.waitlist_count,
            'attendees': AttendeeSerializer(regs, many=True).data,
        })

    @action(detail=True, methods=['post'], url_path='attendees/(?P<reg_id>[^/.]+)/check-in')
    def check_in(self, request, slug=None, reg_id=None):
        """POST /api/events/{slug}/attendees/{reg_id}/check-in/ -> mark an attendee checked in."""
        event = self.get_object()
        self._require_organizer(request, event)
        try:
            reg = event.registrations.get(pk=reg_id)
        except (EventRegistration.DoesNotExist, ValueError, TypeError):
            raise NotFound('Registration not found for this event.')
        if reg.status != EventRegistration.Status.CONFIRMED:
            raise ValidationError('Only confirmed attendees can be checked in.')
        checked = request.data.get('checked_in', True)
        reg.checked_in = bool(checked)
        reg.checked_in_at = timezone.now() if reg.checked_in else None
        reg.save(update_fields=['checked_in', 'checked_in_at', 'updated_at'])
        return Response(AttendeeSerializer(reg).data)
