from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Connection


@admin.register(Connection)
class ConnectionAdmin(ModelAdmin):
    list_display = ['kind', 'sender', 'recipient', 'listing', 'status', 'is_read', 'created_at']
    list_filter = ['kind', 'status', 'is_read']
    search_fields = ['sender__email', 'recipient__email', 'subject', 'message']
    readonly_fields = ['sender', 'recipient', 'listing', 'kind', 'subject', 'message', 'created_at', 'updated_at']
    list_per_page = 20
