from rest_framework import serializers
from .models import ForumCategory, Thread, Reply


def _display_name(user):
    if not user:
        return 'Deleted user'
    full = (user.get_full_name() if hasattr(user, 'get_full_name') else '') or ''
    return full.strip() or user.email.split('@')[0]


class ForumCategorySerializer(serializers.ModelSerializer):
    thread_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ForumCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'order', 'thread_count']


class ReplySerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = ['id', 'author_name', 'body', 'created_at']

    def get_author_name(self, obj):
        return _display_name(obj.author)


class ThreadListSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    reply_count = serializers.IntegerField(read_only=True)
    excerpt = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = [
            'id', 'title', 'slug', 'author_name', 'category_name', 'category_slug',
            'is_pinned', 'is_locked', 'reply_count', 'view_count',
            'excerpt', 'created_at', 'last_activity_at',
        ]

    def get_author_name(self, obj):
        return _display_name(obj.author)

    def get_excerpt(self, obj):
        text = ' '.join(obj.body.split())
        return text[:160] + ('…' if len(text) > 160 else '')


class ThreadDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    category = ForumCategorySerializer(read_only=True)
    replies = ReplySerializer(many=True, read_only=True)
    reply_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Thread
        fields = [
            'id', 'title', 'slug', 'body', 'author_name', 'is_author', 'category',
            'is_pinned', 'is_locked', 'reply_count', 'view_count',
            'created_at', 'last_activity_at', 'replies',
        ]

    def get_author_name(self, obj):
        return _display_name(obj.author)

    def get_is_author(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and
                    (obj.author_id == user.id or user.is_staff))


class ThreadCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=ForumCategory.objects.filter(is_active=True))

    class Meta:
        model = Thread
        fields = ['id', 'slug', 'category', 'title', 'body']
        read_only_fields = ['id', 'slug']

    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError('Please use a more descriptive title (at least 5 characters).')
        return value.strip()

    def validate_body(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError('Your post is too short.')
        return value

    def create(self, validated_data):
        return Thread.objects.create(author=self.context['request'].user, **validated_data)


class ReplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ['id', 'body', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_body(self, value):
        if not value.strip():
            raise serializers.ValidationError('Reply cannot be empty.')
        return value
