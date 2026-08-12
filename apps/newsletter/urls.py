from django.urls import path
from .views import SubscribeView, UnsubscribeView

urlpatterns = [
    path('newsletter/subscribe/', SubscribeView.as_view(), name='newsletter-subscribe'),
    path('newsletter/unsubscribe/', UnsubscribeView.as_view(), name='newsletter-unsubscribe'),
]