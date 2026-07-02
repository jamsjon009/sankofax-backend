from django.db.models import Avg
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Review
from .serializers import ReviewSerializer, OwnerReplySerializer
from apps.directory.models import Listing


class ListingReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return Review.objects.filter(
            listing__slug=self.kwargs['listing_slug'],
            status=Review.Status.APPROVED,
        )

    def perform_create(self, serializer):
        listing = Listing.objects.get(slug=self.kwargs['listing_slug'])
        review = serializer.save(listing=listing, user=self.request.user)
        self._update_listing_stats(listing)

    def _update_listing_stats(self, listing):
        qs = Review.objects.filter(listing=listing, status=Review.Status.APPROVED)
        agg = qs.aggregate(avg=Avg('rating'))
        listing.avg_rating = agg['avg'] or 0
        listing.review_count = qs.count()
        listing.save(update_fields=['avg_rating', 'review_count'])


class OwnerReplyView(generics.UpdateAPIView):
    serializer_class = OwnerReplySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Review.objects.all()

    def perform_update(self, serializer):
        serializer.save(owner_reply_at=timezone.now())
