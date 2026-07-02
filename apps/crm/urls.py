from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeadViewSet, SupportTicketViewSet, PendingListingsViewSet

router = DefaultRouter()
router.register('crm/leads', LeadViewSet, basename='lead')
router.register('crm/tickets', SupportTicketViewSet, basename='ticket')
router.register('crm/listings', PendingListingsViewSet, basename='crm-listings')

urlpatterns = [path('', include(router.urls))]
