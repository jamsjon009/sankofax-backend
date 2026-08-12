from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.directory.models import Listing
from apps.directory.serializers import ListingDetailSerializer
from .models import Lead, LeadNote, SupportTicket
from .serializers import LeadSerializer, LeadNoteSerializer, SupportTicketSerializer


class IsStaffOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin_or_staff


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.prefetch_related('notes').all()
    serializer_class = LeadSerializer
    permission_classes = [IsStaffOrAdmin]
    search_fields = ['name', 'email']
    filterset_fields = ['status', 'source', 'assigned_to']

    @action(detail=True, methods=['post'], url_path='notes')
    def add_note(self, request, pk=None):
        lead = self.get_object()
        serializer = LeadNoteSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(lead=lead)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        lead = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Lead.Status.choices):
            return Response({'detail': 'Invalid status.'}, status=400)
        lead.status = new_status
        lead.save(update_fields=['status'])
        return Response({'status': lead.status})


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
        from rest_framework.pagination import PageNumberPagination
        qs = Listing.objects.filter(listing_status=Listing.Status.PENDING).select_related('company', 'category')
        paginator = PageNumberPagination()
        paginator.page_size = 12
        page = paginator.paginate_queryset(qs, request)
        serializer = ListingDetailSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

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
