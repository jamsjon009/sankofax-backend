from django.urls import path
from .views import (
    UserProfileView, CompanyListCreateView, CompanyDetailView, IdentityBadgeListView,
)

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('badges/', IdentityBadgeListView.as_view(), name='badge-list'),
    path('companies/', CompanyListCreateView.as_view(), name='company-list'),
    path('companies/<slug:slug>/', CompanyDetailView.as_view(), name='company-detail'),
]
