from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import ForumCategory, Thread, Reply


@admin.register(ForumCategory)
class ForumCategoryAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active', 'thread_count']
    list_editable = ['order', 'is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class ReplyInline(admin.TabularInline):
    model = Reply
    extra = 0
    fields = ['author', 'body', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Thread)
class ThreadAdmin(ModelAdmin):
    list_display = ['title', 'category', 'author', 'is_pinned', 'is_locked', 'reply_count', 'view_count', 'last_activity_at']
    list_filter = ['category', 'is_pinned', 'is_locked']
    search_fields = ['title', 'body', 'author__email']
    readonly_fields = ['slug', 'view_count', 'created_at', 'updated_at', 'last_activity_at']
    inlines = [ReplyInline]
    actions = ['pin_threads', 'unpin_threads', 'lock_threads', 'unlock_threads']

    @admin.action(description='Pin selected threads')
    def pin_threads(self, request, queryset):
        queryset.update(is_pinned=True)

    @admin.action(description='Unpin selected threads')
    def unpin_threads(self, request, queryset):
        queryset.update(is_pinned=False)

    @admin.action(description='Lock selected threads (no new replies)')
    def lock_threads(self, request, queryset):
        queryset.update(is_locked=True)

    @admin.action(description='Unlock selected threads')
    def unlock_threads(self, request, queryset):
        queryset.update(is_locked=False)


@admin.register(Reply)
class ReplyAdmin(ModelAdmin):
    list_display = ['thread', 'author', 'created_at']
    search_fields = ['body', 'author__email', 'thread__title']
    readonly_fields = ['created_at', 'updated_at']
