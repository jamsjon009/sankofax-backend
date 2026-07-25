from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Connection
from .serializers import ConnectionSerializer, ConnectionCreateSerializer


class ConnectionListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/connections/?box=inbox  -> requests received by me (default)
    GET  /api/connections/?box=sent   -> requests I sent
    POST /api/connections/            -> send a connect / collaborate request
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return ConnectionCreateSerializer if self.request.method == 'POST' else ConnectionSerializer

    def get_queryset(self):
        user = self.request.user
        box = self.request.query_params.get('box', 'inbox')
        qs = Connection.objects.select_related('sender', 'recipient', 'listing', 'listing__company')
        if box == 'sent':
            return qs.filter(sender=user)
        return qs.filter(recipient=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response(ConnectionSerializer(obj).data, status=status.HTTP_201_CREATED)


class ConnectionDetailView(generics.RetrieveUpdateAPIView):
    """
    PATCH /api/connections/{id}/ -> recipient accepts/declines (status) or marks read.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConnectionSerializer

    def get_queryset(self):
        user = self.request.user
        return Connection.objects.filter(recipient=user) | Connection.objects.filter(sender=user)

    def patch(self, request, *args, **kwargs):
        obj = self.get_object()
        # Only the recipient may change status or mark as read.
        if obj.recipient_id != request.user.id:
            return Response({'detail': 'Only the recipient can update this request.'},
                            status=status.HTTP_403_FORBIDDEN)
        new_status = request.data.get('status')
        if new_status in (Connection.Status.ACCEPTED, Connection.Status.DECLINED):
            obj.status = new_status
        if 'is_read' in request.data:
            obj.is_read = bool(request.data.get('is_read'))
        obj.save()
        return Response(ConnectionSerializer(obj).data)


class ConnectionUnreadCountView(APIView):
    """GET /api/connections/unread-count/ -> number of unread inbox requests."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Connection.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'unread': count})
