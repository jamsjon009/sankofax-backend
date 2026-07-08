from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from .models import Category, Amenity, Listing, ListingImage


class ListingImageInline(TabularInline):
    model = ListingImage
    extra = 1
    fields = ['image_preview', 'image', 'caption', 'order']
    readonly_fields = ['image_preview']

    @admin.display(description='Preview')
    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="width:60px;height:45px;object-fit:cover;border-radius:4px;" />',
                obj.image.url,
            )
        return '—'


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['thumbnail', 'name', 'slug', 'listing_type', 'parent', 'order']
    list_per_page = 10
    list_filter = ['listing_type', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    fields = ['name', 'slug', 'icon', 'description', 'cover_image', 'parent', 'listing_type', 'order']

    @admin.display(description='Image')
    def thumbnail(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="width:60px;height:40px;object-fit:cover;border-radius:4px;" />',
                obj.cover_image.url,
            )
        return '—'


@admin.register(Amenity)
class AmenityAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    list_per_page = 10
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Listing)
class ListingAdmin(ModelAdmin):
    list_display = ['thumbnail', 'title', 'company', 'category', 'listing_status', 'city', 'featured', 'avg_rating', 'created_at']
    list_per_page = 10
    list_filter = ['listing_status', 'featured', 'category', 'country']
    search_fields = ['title', 'company__company_name', 'city', 'country']
    readonly_fields = ['slug', 'avg_rating', 'review_count', 'view_count', 'created_at', 'updated_at', 'published_at']
    inlines = [ListingImageInline]
    actions = ['approve_listings', 'reject_listings', 'feature_listings']

    fieldsets = (
        ('Basic Info', {'fields': ('company', 'category', 'secondary_categories', 'title', 'slug', 'short_description', 'full_description')}),
        ('Status', {'fields': ('listing_status', 'featured', 'featured_until', 'reviewed_by', 'rejection_reason')}),
        ('Location', {'fields': ('address_line', 'city', 'state', 'country', 'postal_code', 'latitude', 'longitude')}),
        ('Contact', {'fields': ('phone', 'email', 'website', 'whatsapp')}),
        ('Details', {'fields': ('price_range', 'opening_hours', 'amenities')}),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'og_image'),
            'classes': ('collapse',),
        }),
        ('Stats', {'fields': ('avg_rating', 'review_count', 'view_count')}),
        ('Dates', {'fields': ('created_at', 'updated_at', 'published_at')}),
    )

    @admin.display(description='Image')
    def thumbnail(self, obj):
        first = obj.gallery_images.first()
        if first and first.image:
            return format_html(
                '<img src="{}" style="width:60px;height:40px;object-fit:cover;border-radius:4px;" />',
                first.image.url,
            )
        return '—'

    @admin.action(description='Approve selected listings')
    def approve_listings(self, request, queryset):
        queryset.update(listing_status=Listing.Status.PUBLISHED, published_at=timezone.now(), reviewed_by=request.user)

    @admin.action(description='Reject selected listings')
    def reject_listings(self, request, queryset):
        queryset.update(listing_status=Listing.Status.REJECTED, reviewed_by=request.user)

    @admin.action(description='Mark as Featured')
    def feature_listings(self, request, queryset):
        queryset.update(featured=True)
