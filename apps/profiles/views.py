from rest_framework import generics, permissions
from .models import UserProfile, CompanyProfile, IdentityBadge
from .serializers import (
    UserProfileSerializer, CompanyProfileSerializer,
    CompanyProfileCreateSerializer, IdentityBadgeSerializer,
)


class IdentityBadgeListView(generics.ListAPIView):
    """Public list of all identity/ownership badges (for filters and forms)."""
    queryset = IdentityBadge.objects.all()
    serializer_class = IdentityBadgeSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class CompanyListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CompanyProfile.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CompanyProfileCreateSerializer
        return CompanyProfileSerializer


class CompanyDetailView(generics.RetrieveUpdateAPIView):
    queryset = CompanyProfile.objects.all()
    serializer_class = CompanyProfileSerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return CompanyProfileSerializer
        return CompanyProfileCreateSerializer
