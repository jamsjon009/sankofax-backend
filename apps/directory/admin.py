from django.contrib import admin
from django.utils import timezone
from unfold.admin import ModelAdmin, TabularInline
from .models import Category, Amenity, Listing, ListingImage


class ListingImageInline(TabularInline):
    model = ListingImage
    extra = 1
    fields = ['image', 'caption', 'order']


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'listing_type', 'parent', 'order']
    list_filter = ['listing_type', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(Amenity)
class AmenityAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Listing)
class ListingAdmin(ModelAdmin):
    list_display = ['title', 'company', 'category', 'listing_status', 'city', 'country', 'featured', 'avg_rating', 'created_at']
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
        ('Stats', {'fields': ('avg_rating', 'review_count', 'view_count')}),
        ('Dates', {'fields': ('created_at', 'updated_at', 'published_at')}),
    )

    @admin.action(description='Approve selected listings')
    def approve_listings(self, request, queryset):
        queryset.update(listing_status=Listing.Status.PUBLISHED, published_at=timezone.now(), reviewed_by=request.user)

    @admin.action(description='Reject selected listings')
    def reject_listings(self, request, queryset):
        queryset.update(listing_status=Listing.Status.REJECTED, reviewed_by=request.user)

    @admin.action(description='Mark as Featured')
    def feature_listings(self, request, queryset):
        queryset.update(featured=True)
