from django.urls import path
from .views import ListingReviewListCreateView, OwnerReplyView

urlpatterns = [
    path('listings/<slug:listing_slug>/reviews/', ListingReviewListCreateView.as_view(), name='listing-reviews'),
    path('reviews/<int:pk>/reply/', OwnerReplyView.as_view(), name='review-reply'),
]
