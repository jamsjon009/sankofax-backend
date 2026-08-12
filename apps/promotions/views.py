from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import StoryPackage, StorySubmission
from .serializers import (
    StoryPackageSerializer, StorySubmissionSerializer, StorySubmissionCreateSerializer,
)
from . import payments


class StoryPackageListView(generics.ListAPIView):
    """Public list of active promotion packages (prices reflect the caller's subscriber discount)."""
    serializer_class = StoryPackageSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return StoryPackage.objects.filter(is_active=True)


class StorySubmissionListCreateView(APIView):
    """
    GET  /api/promotions/submissions/ -> the current user's submissions.
    POST /api/promotions/submissions/ -> submit a story + start Stripe checkout (multipart).
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        qs = StorySubmission.objects.select_related('package', 'company', 'published_post')
        if request.query_params.get('all') and request.user.is_staff:
            pass  # staff can list everything
        else:
            qs = qs.filter(submitted_by=request.user)
        return Response(StorySubmissionSerializer(qs, many=True).data)

    def post(self, request):
        data = StorySubmissionCreateSerializer(data=request.data, context={'request': request})
        data.is_valid(raise_exception=True)
        v = data.validated_data
        package = v['package']

        amount = package.price_for(request.user)
        submission = StorySubmission.objects.create(
            package=package,
            company=v['company'],
            submitted_by=request.user,
            kind=package.kind,
            title=v['title'],
            body=v['body'],
            contact_email=v['contact_email'],
            cover_image=v.get('cover_image'),
            amount=amount,
            currency=package.currency,
            status=StorySubmission.Status.PENDING_PAYMENT,
        )

        try:
            checkout_url = payments.create_submission_checkout(submission)
        except Exception as e:  # noqa: BLE001 — clean error, drop the dangling submission
            submission.delete()
            raise ValidationError(f'Could not start checkout: {e}')

        return Response(
            {'checkout_url': checkout_url, 'submission': StorySubmissionSerializer(submission).data},
            status=status.HTTP_201_CREATED,
        )


class StorySubmissionDetailView(generics.RetrieveAPIView):
    """GET /api/promotions/submissions/<reference>/ -> one of my submissions."""
    serializer_class = StorySubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'reference'

    def get_queryset(self):
        qs = StorySubmission.objects.select_related('package', 'company', 'published_post')
        if self.request.user.is_staff:
            return qs
        return qs.filter(submitted_by=self.request.user)
