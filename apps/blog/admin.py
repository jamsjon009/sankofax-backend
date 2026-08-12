from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models import BlogPost, BlogCategory


@admin.register(BlogCategory)
class BlogCategoryAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'post_count', 'order']
    list_per_page = 10
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    list_display = ['title', 'category', 'author', 'status', 'is_featured', 'view_count', 'published_at']
    list_per_page = 10
    list_filter = ['status', 'is_featured', 'category']
    search_fields = ['title', 'excerpt', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'created_at', 'updated_at', 'cover_preview']
    ordering = ['-created_at']
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'category', 'tags', 'status', 'is_featured', 'published_at'),
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'read_time_minutes'),
        }),
        ('Images', {
            'fields': ('cover_image', 'cover_preview'),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'og_image'),
            'classes': ('collapse',),
        }),
        ('Stats', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height:120px;border-radius:8px;">', obj.cover_image.url)
        return '-'
    cover_preview.short_description = 'Cover Preview'