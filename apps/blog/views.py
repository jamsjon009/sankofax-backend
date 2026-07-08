from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import BlogPost, BlogCategory
from .serializers import BlogPostListSerializer, BlogPostDetailSerializer, BlogCategorySerializer


class BlogPostListView(generics.ListAPIView):
    serializer_class = BlogPostListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'is_featured']
    search_fields = ['title', 'excerpt', 'tags']
    ordering_fields = ['published_at', 'view_count']

    def get_queryset(self):
        return BlogPost.objects.filter(
            status=BlogPost.Status.PUBLISHED
        ).select_related('author', 'category')


class BlogPostDetailView(generics.RetrieveAPIView):
    serializer_class = BlogPostDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return BlogPost.objects.filter(
            status=BlogPost.Status.PUBLISHED
        ).select_related('author', 'category')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        BlogPost.objects.filter(pk=instance.pk).update(view_count=instance.view_count + 1)
        serializer = self.get_serializer(instance)
        return __import__('rest_framework.response', fromlist=['Response']).Response(serializer.data)


class BlogCategoryListView(generics.ListAPIView):
    serializer_class = BlogCategorySerializer
    permission_classes = [AllowAny]
    queryset = BlogCategory.objects.all()
    pagination_class = None  # plain array, categories are few