from django.utils import timezone
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Amenity, Listing
from .serializers import (
    CategorySerializer, AmenitySerializer,
    ListingCardSerializer, ListingDetailSerializer, ListingCreateUpdateSerializer,
)
from .filters import ListingFilter
from apps.accounts.permissions import IsBusinessOwner


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(parent=None).prefetch_related('subcategories')
    pagination_class = None  # plain array
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class AmenityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # plain array
    lookup_field = 'slug'


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.filter(listing_status=Listing.Status.PUBLISHED).select_related(
        'category', 'company'
    ).prefetch_related('gallery_images', 'amenities')
    filterset_class = ListingFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'short_description', 'city', 'country', 'company__company_name']
    ordering_fields = ['avg_rating', 'review_count', 'created_at', 'view_count']
    ordering = ['-featured', '-avg_rating']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return ListingCardSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ListingCreateUpdateSerializer
        return ListingDetailSerializer

    def get_permissions(self):
        # Creating a listing is a business-owner action; edits/deletes are
        # further scoped to the owner's own listings in get_queryset().
        if self.action in ['create']:
            return [IsBusinessOwner()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsBusinessOwner()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            if self.request.user.is_authenticated and self.request.user.is_admin_or_staff:
                return Listing.objects.all().select_related('category', 'company').prefetch_related('gallery_images', 'amenities')
            return Listing.objects.filter(company__owner=self.request.user).select_related('category', 'company').prefetch_related('gallery_images', 'amenities')

        # ?my=true returns the authenticated user's own listings regardless of status
        if self.request.query_params.get('my') == 'true' and self.request.user.is_authenticated:
            return Listing.objects.filter(company__owner=self.request.user).select_related('category', 'company').prefetch_related('gallery_images', 'amenities')

        return Listing.objects.filter(listing_status=Listing.Status.PUBLISHED).select_related('category', 'company').prefetch_related('gallery_images', 'amenities')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Listing.objects.filter(pk=instance.pk).update(view_count=instance.view_count + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def saved(self, request):
        """GET /api/listings/saved/ — the current user's saved (bookmarked) listings."""
        from apps.profiles.models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        qs = (profile.saved_listings
              .filter(listing_status=Listing.Status.PUBLISHED)
              .select_related('category', 'company')
              .prefetch_related('gallery_images', 'amenities'))
        page = self.paginate_queryset(qs)
        serializer = ListingCardSerializer(page if page is not None else qs, many=True, context={'request': request})
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def save_listing(self, request, slug=None):
        listing = self.get_object()
        profile = request.user.profile
        if listing in profile.saved_listings.all():
            profile.saved_listings.remove(listing)
            return Response({'saved': False})
        profile.saved_listings.add(listing)
        return Response({'saved': True})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='images')
    def upload_image(self, request, slug=None):
        from .models import ListingImage
        from .serializers import ListingImageSerializer
        listing = Listing.objects.get(slug=slug)
        if not (request.user.is_admin_or_staff or listing.company.owner == request.user):
            return Response({'detail': 'Permission denied.'}, status=403)
        img = ListingImage.objects.create(
            listing=listing,
            image=request.FILES.get('image'),
            caption=request.data.get('caption', ''),
            order=request.data.get('order', 0),
        )
        return Response(ListingImageSerializer(img).data, status=201)
