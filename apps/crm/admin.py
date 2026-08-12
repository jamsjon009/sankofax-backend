from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Lead, LeadNote, SupportTicket


class LeadNoteInline(TabularInline):
    model = LeadNote
    extra = 0
    fields = ['author', 'body', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Lead)
class LeadAdmin(ModelAdmin):
    list_display = ['name', 'email', 'source', 'status', 'assigned_to', 'created_at']
    list_per_page = 10
    list_filter = ['status', 'source', 'assigned_to']
    search_fields = ['name', 'email']
    inlines = [LeadNoteInline]


@admin.register(SupportTicket)
class SupportTicketAdmin(ModelAdmin):
    list_display = ['subject', 'user', 'status', 'priority', 'assigned_to', 'created_at']
    list_per_page = 10
    list_filter = ['status', 'priority', 'assigned_to']
    search_fields = ['subject', 'user__email']
