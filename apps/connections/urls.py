from django.urls import path
from .views import ConnectionListCreateView, ConnectionDetailView, ConnectionUnreadCountView

urlpatterns = [
    path('connections/', ConnectionListCreateView.as_view(), name='connection-list'),
    path('connections/unread-count/', ConnectionUnreadCountView.as_view(), name='connection-unread'),
    path('connections/<uuid:pk>/', ConnectionDetailView.as_view(), name='connection-detail'),
]
