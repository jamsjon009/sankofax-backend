from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import SiteSetting, Page, FAQ


@admin.register(SiteSetting)
class SiteSettingAdmin(ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Page)
class PageAdmin(ModelAdmin):
    list_display = ['title', 'slug', 'is_active', 'updated_at']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(FAQ)
class FAQAdmin(ModelAdmin):
    list_display = ['question', 'order', 'is_active']
    list_editable = ['order', 'is_active']
