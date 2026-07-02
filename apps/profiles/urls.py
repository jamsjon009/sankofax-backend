from django.urls import path
from .views import UserProfileView, CompanyListCreateView, CompanyDetailView

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('companies/', CompanyListCreateView.as_view(), name='company-list'),
    path('companies/<slug:slug>/', CompanyDetailView.as_view(), name='company-detail'),
]
