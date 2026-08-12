from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import ForumCategory, Thread, Reply
from .serializers import (
    ForumCategorySerializer, ThreadListSerializer, ThreadDetailSerializer,
    ThreadCreateSerializer, ReplySerializer, ReplyCreateSerializer,
)


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)


class ForumCategoryListView(generics.ListAPIView):
    """Public list of active discussion boards."""
    serializer_class = ForumCategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return ForumCategory.objects.filter(is_active=True)


class ThreadListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/community/threads/            -> list (filter: ?category=slug, ?q=search)
    POST /api/community/threads/            -> start a discussion (auth)
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        return ThreadCreateSerializer if self.request.method == 'POST' else ThreadListSerializer

    def get_queryset(self):
        qs = Thread.objects.select_related('author', 'category')
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category__slug=category)
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(title__icontains=q) | qs.filter(body__icontains=q)
        return qs.distinct()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        thread = serializer.save()
        return Response(ThreadDetailSerializer(thread).data, status=status.HTTP_201_CREATED)


class ThreadDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    /api/community/threads/{slug}/  -> thread + replies (public, bumps view count)
    DELETE /api/community/threads/{slug}/  -> delete (author or staff only)
    """
    serializer_class = ThreadDetailSerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return Thread.objects.select_related('author', 'category').prefetch_related(
            'replies__author')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Thread.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        instance.view_count += 1
        return Response(self.get_serializer(instance).data)

    def perform_destroy(self, instance):
        user = self.request.user
        if instance.author_id != user.id and not user.is_staff:
            raise PermissionDenied('You can only delete your own discussions.')
        instance.delete()


class ReplyListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/community/threads/{slug}/replies/  -> replies
    POST /api/community/threads/{slug}/replies/  -> add a reply (auth)
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        return ReplyCreateSerializer if self.request.method == 'POST' else ReplySerializer

    def _get_thread(self):
        return get_object_or_404(Thread, slug=self.kwargs['slug'])

    def get_queryset(self):
        return Reply.objects.filter(thread__slug=self.kwargs['slug']).select_related('author')

    def create(self, request, *args, **kwargs):
        thread = self._get_thread()
        if thread.is_locked:
            raise ValidationError('This discussion is locked and no longer accepts replies.')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reply = serializer.save(thread=thread, author=request.user)
        # Bump thread activity so it sorts to the top of the list.
        Thread.objects.filter(pk=thread.pk).update(last_activity_at=timezone.now())
        return Response(ReplySerializer(reply).data, status=status.HTTP_201_CREATED)
