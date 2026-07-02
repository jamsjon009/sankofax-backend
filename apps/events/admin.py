from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Event


@admin.register(Event)
class EventAdmin(ModelAdmin):
    list_display = ['title', 'organizer', 'city', 'country', 'start_datetime', 'status']
    list_filter = ['status', 'is_virtual', 'country']
    search_fields = ['title', 'organizer__company_name', 'city']
    readonly_fields = ['slug', 'created_at']
