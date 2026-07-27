from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, ServiceViewSet, CheckoutView,
    OrderListView, OrderDetailView, BookingListCreateView, BookingDetailView,
)

router = DefaultRouter()
router.register('marketplace/services', ServiceViewSet, basename='service')
router.register('marketplace', ProductViewSet, basename='product')

urlpatterns = [
    # Explicit routes first so they win over the product router's /marketplace/<slug>/.
    path('marketplace/checkout/', CheckoutView.as_view(), name='marketplace-checkout'),
    path('marketplace/orders/', OrderListView.as_view(), name='marketplace-orders'),
    path('marketplace/orders/<str:order_number>/', OrderDetailView.as_view(), name='marketplace-order-detail'),
    path('marketplace/bookings/', BookingListCreateView.as_view(), name='marketplace-bookings'),
    path('marketplace/bookings/<str:booking_number>/', BookingDetailView.as_view(), name='marketplace-booking-detail'),
    path('', include(router.urls)),
]
