from django.urls import path
from .views import (
    UserProfileView, CompanyListCreateView, CompanyDetailView, IdentityBadgeListView,
    VerificationStatusView, VerificationRequestListCreateView,
)

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('badges/', IdentityBadgeListView.as_view(), name='badge-list'),
    path('companies/', CompanyListCreateView.as_view(), name='company-list'),
    path('companies/<slug:slug>/', CompanyDetailView.as_view(), name='company-detail'),
    # Verification tiers & workflow
    path('verification/requests/', VerificationRequestListCreateView.as_view(),
         name='verification-requests'),
    path('verification/companies/<slug:slug>/', VerificationStatusView.as_view(),
         name='verification-status'),
]
