from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import SiteSetting, HomeContent, Page, FAQ, Testimonial


@admin.register(HomeContent)
class HomeContentAdmin(ModelAdmin):
    fieldsets = [
        ('Hero', {'fields': ['hero_badge', 'hero_title', 'hero_title_highlight',
                             'hero_subtitle', 'hero_popular_searches']}),
        ('Why List Your Brand', {'fields': ['why_list_title', 'why_list_subtitle', 'why_list_benefits'],
            'description': 'Benefits is a list of {"title", "desc"} cards — the five card icons are fixed in the design.'}),
        ('Mission & Vision', {'fields': ['mission_title', 'mission_body', 'vision_title', 'vision_body']}),
        ('Pricing Section', {'fields': ['pricing_title', 'pricing_subtitle', 'pricing_note'],
            'description': 'Intro copy above the pricing table. The plans/prices themselves live under Subscriptions → Plans.'}),
        ('Call to Action', {'fields': ['cta_title', 'cta_subtitle']}),
        ('Newsletter', {'fields': ['newsletter_title', 'newsletter_subtitle']}),
    ]

    def has_add_permission(self, request):
        return not HomeContent.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteSetting)
class SiteSettingAdmin(ModelAdmin):
    fieldsets = [
        ('General', {'fields': ['site_name', 'logo', 'meta_description', 'default_og_image', 'footer_text']}),
        ('Contact Information', {'fields': ['contact_email', 'contact_phone', 'contact_address', 'response_time', 'map_embed_code'],
            'description': 'These appear on the Contact page. Map: Google Maps → Share → Embed a map → copy the full &lt;iframe&gt; code and paste it here.'}),
        ('Social Media Links', {'fields': ['instagram_url', 'facebook_url', 'twitter_url', 'linkedin_url', 'youtube_url', 'tiktok_url'],
            'description': 'Full URLs e.g. https://instagram.com/sankofax — leave blank to hide that icon.'}),
        ('Instagram Feed (Footer)', {'fields': ['instagram_embed_code'],
            'description': 'Show your real Instagram posts in the footer. Go to snapwidget.com or lightwidget.com, '
                           'connect your Instagram account, copy the generated &lt;iframe&gt; embed code, and paste it here. '
                           'Leave blank to keep the default placeholder tiles.'}),
        ('Analytics & Tags', {'fields': ['google_tag_manager_id', 'google_analytics_id', 'google_search_console_code'],
            'description': 'Enter GTM ID (e.g. GTM-XXXXXXX) to enable Google Tag Manager. GA4 ID only needed if NOT using GTM.'}),
    ]

    def has_add_permission(self, request):
        return not SiteSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Page)
class PageAdmin(ModelAdmin):
    list_display = ['title', 'slug', 'is_active', 'updated_at']
    list_per_page = 10
    prepopulated_fields = {'slug': ('title',)}


@admin.register(FAQ)
class FAQAdmin(ModelAdmin):
    list_display = ['question', 'order', 'is_active']
    list_per_page = 10
    list_editable = ['order', 'is_active']


@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ['user', 'short_body', 'role', 'status', 'order', 'created_at']
    list_filter = ['status']
    list_editable = ['status', 'order']
    list_per_page = 20
    readonly_fields = ['user', 'body', 'role', 'created_at']
    actions = ['approve', 'reject']

    @admin.display(description='Testimonial')
    def short_body(self, obj):
        return obj.body[:80] + '…' if len(obj.body) > 80 else obj.body

    @admin.action(description='Approve selected testimonials')
    def approve(self, request, queryset):
        queryset.update(status=Testimonial.Status.APPROVED)

    @admin.action(description='Reject selected testimonials')
    def reject(self, request, queryset):
        queryset.update(status=Testimonial.Status.REJECTED)
