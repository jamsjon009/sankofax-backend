from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, AmenityViewSet, ListingViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('amenities', AmenityViewSet, basename='amenity')
router.register('listings', ListingViewSet, basename='listing')

urlpatterns = [
    path('', include(router.urls)),
]
