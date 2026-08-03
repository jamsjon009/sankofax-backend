from django.contrib import admin
from django.utils import timezone
from unfold.admin import ModelAdmin, TabularInline
from .models import Event, EventRegistration


class EventRegistrationInline(TabularInline):
    model = EventRegistration
    extra = 0
    fields = ['name', 'email', 'quantity', 'status', 'ticket_code', 'checked_in', 'created_at']
    readonly_fields = ['ticket_code', 'created_at']
    ordering = ['status', 'created_at']


@admin.register(Event)
class EventAdmin(ModelAdmin):
    list_display = ['title', 'organizer', 'city', 'country', 'start_datetime', 'status',
                    'rsvp_enabled', 'capacity']
    list_per_page = 10
    list_filter = ['status', 'is_virtual', 'rsvp_enabled', 'country']
    search_fields = ['title', 'organizer__company_name', 'city']
    readonly_fields = ['slug', 'created_at']
    inlines = [EventRegistrationInline]
    actions = ['geocode_selected']

    @admin.action(description='Geocode selected (address → map coordinates)')
    def geocode_selected(self, request, queryset):
        from apps.core.geocoding import geocode_event
        updated = sum(1 for obj in queryset if geocode_event(obj, force=True))
        self.message_user(request, f'Geocoded {updated} of {queryset.count()} event(s).')


@admin.register(EventRegistration)
class EventRegistrationAdmin(ModelAdmin):
    list_display = ['name', 'event', 'quantity', 'status', 'ticket_code', 'checked_in', 'created_at']
    list_per_page = 25
    list_filter = ['status', 'checked_in', 'event']
    search_fields = ['name', 'email', 'ticket_code', 'event__title']
    readonly_fields = ['ticket_code', 'created_at', 'updated_at']
    autocomplete_fields = ['event']
    raw_id_fields = ['attendee']
    actions = ['mark_checked_in', 'mark_not_checked_in']

    @admin.action(description='Mark selected as checked in')
    def mark_checked_in(self, request, queryset):
        n = queryset.update(checked_in=True, checked_in_at=timezone.now())
        self.message_user(request, f'{n} attendee(s) checked in.')

    @admin.action(description='Mark selected as NOT checked in')
    def mark_not_checked_in(self, request, queryset):
        n = queryset.update(checked_in=False, checked_in_at=None)
        self.message_user(request, f'{n} attendee(s) reset.')
