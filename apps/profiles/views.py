from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from .models import UserProfile, CompanyProfile, IdentityBadge, VerificationRequest
from .serializers import (
    UserProfileSerializer, CompanyProfileSerializer,
    CompanyProfileCreateSerializer, IdentityBadgeSerializer,
    VerificationRequestSerializer,
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


def _verification_status_payload(company):
    """Serializable summary of a company's verification state + requirements."""
    checks = company.automated_check_results()
    latest = company.verification_requests.first()
    return {
        'company_slug': company.slug,
        'company_name': company.company_name,
        'verification_level': company.verification_level,
        'verification_label': company.verification_label,
        'verified_at': company.verified_at,
        'verification_expires_at': company.verification_expires_at,
        'is_expired': company.is_verification_expired,
        'automated_checks': [
            {'key': key, 'label': label, 'passed': checks[key]}
            for key, label in company.AUTOMATED_CHECKS
        ],
        'passes_automated': company.passes_automated_checks(),
        'has_pending': company.verification_requests.filter(
            status=VerificationRequest.Status.PENDING).exists(),
        'latest_request': VerificationRequestSerializer(latest).data if latest else None,
    }


class VerificationStatusView(APIView):
    """Owner-only summary of a company's verification tier, checks and latest request."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, slug):
        company = get_object_or_404(CompanyProfile, slug=slug, owner=request.user)
        return Response(_verification_status_payload(company))


class VerificationRequestListCreateView(APIView):
    """List the owner's verification requests, or submit a new one.

    Level 1 (Basic) is resolved immediately from automated checks. Levels 2 and 3
    create a pending request for admin review (documents required).
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        qs = VerificationRequest.objects.filter(company__owner=request.user)
        slug = request.query_params.get('company')
        if slug:
            qs = qs.filter(company__slug=slug)
        return Response(VerificationRequestSerializer(qs, many=True).data)

    def post(self, request):
        slug = request.data.get('company')
        if not slug:
            raise ValidationError({'company': 'This field is required.'})
        try:
            company = CompanyProfile.objects.get(slug=slug, owner=request.user)
        except CompanyProfile.DoesNotExist:
            raise NotFound('Company not found or not owned by you.')

        try:
            level = int(request.data.get('requested_level', 0))
        except (TypeError, ValueError):
            raise ValidationError({'requested_level': 'Must be 1, 2 or 3.'})
        if level not in (1, 2, 3):
            raise ValidationError({'requested_level': 'Must be 1, 2 or 3.'})

        if level <= company.verification_level and not company.is_verification_expired:
            raise ValidationError(
                {'requested_level': f'Company is already at level {company.verification_level} or higher.'})

        if company.verification_requests.filter(status=VerificationRequest.Status.PENDING).exists():
            raise ValidationError(
                {'detail': 'You already have a verification request pending review.'})

        note = (request.data.get('note') or '').strip()

        # Level 1 — automated, resolved immediately.
        if level == 1:
            req = VerificationRequest.objects.create(
                company=company, requested_level=1, note=note)
            if company.passes_automated_checks():
                req.approve(notes='Automated checks passed.')
            else:
                failed = [label for key, label in company.AUTOMATED_CHECKS
                          if not company.automated_check_results()[key]]
                req.reject(notes='Automated checks failed: ' + '; '.join(failed) + '.')
            return Response(
                {'request': VerificationRequestSerializer(req).data,
                 'status': _verification_status_payload(company)},
                status=201)

        # Levels 2 & 3 — document / partner review.
        if not request.data.get('documents'):
            raise ValidationError(
                {'documents': 'Ownership / registration documents are required for this tier.'})

        req = VerificationRequest.objects.create(
            company=company, requested_level=level,
            documents=request.data.get('documents'), note=note)
        return Response(
            {'request': VerificationRequestSerializer(req).data,
             'status': _verification_status_payload(company)},
            status=201)
