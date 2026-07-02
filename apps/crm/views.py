from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.directory.models import Listing
from apps.directory.serializers import ListingDetailSerializer
from .models import Lead, SupportTicket
from .serializers import LeadSerializer, SupportTicketSerializer


class IsStaffOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin_or_staff


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.prefetch_related('notes').all()
    serializer_class = LeadSerializer
    permission_classes = [IsStaffOrAdmin]
    search_fields = ['name', 'email']
    filterset_fields = ['status', 'source', 'assigned_to']


class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    filterset_fields = ['status', 'priority']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [IsStaffOrAdmin()]

    def get_queryset(self):
        if self.request.user.is_admin_or_staff:
            return SupportTicket.objects.all()
        return SupportTicket.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = SupportTicket.Status.RESOLVED
        ticket.resolved_at = timezone.now()
        ticket.save()
        return Response({'status': 'resolved'})


class PendingListingsViewSet(viewsets.ViewSet):
    permission_classes = [IsStaffOrAdmin]

    def list(self, request):
        qs = Listing.objects.filter(listing_status=Listing.Status.PENDING).select_related('company', 'category')
        return Response(ListingDetailSerializer(qs, many=True, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        listing = Listing.objects.get(pk=pk)
        listing.listing_status = Listing.Status.PUBLISHED
        listing.reviewed_by = request.user
        listing.save()
        return Response({'status': 'published'})

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        listing = Listing.objects.get(pk=pk)
        listing.listing_status = Listing.Status.REJECTED
        listing.reviewed_by = request.user
        listing.rejection_reason = request.data.get('reason', '')
        listing.save()
        return Response({'status': 'rejected'})
