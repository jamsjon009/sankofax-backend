from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Subscriber


@admin.register(Subscriber)
class SubscriberAdmin(ModelAdmin):
    list_display = ['email', 'source', 'is_active', 'subscribed_at']
    list_filter = ['source', 'is_active']
    search_fields = ['email']
    actions = ['export_csv']

    @admin.action(description='Export selected as CSV')
    def export_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=subscribers.csv'
        writer = csv.writer(response)
        writer.writerow(['email', 'source', 'subscribed_at'])
        for sub in queryset:
            writer.writerow([sub.email, sub.source, sub.subscribed_at])
        return response
