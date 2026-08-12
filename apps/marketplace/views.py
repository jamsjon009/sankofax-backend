from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.permissions import IsBusinessOwner
from .models import Product, Service, Order, OrderItem, ServiceBooking
from .serializers import (
    ProductSerializer, ServiceSerializer, OrderSerializer, ServiceBookingSerializer,
    CheckoutSerializer, BookingCreateSerializer,
)
from . import payments


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('company', 'category').prefetch_related('images')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'stock_status', 'company']
    search_fields = ['name', 'description', 'company__company_name']
    ordering_fields = ['price', 'created_at']
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsBusinessOwner()]
        return [permissions.AllowAny()]


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.filter(is_active=True).select_related('company', 'category')
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'company', 'is_virtual']
    search_fields = ['name', 'description', 'company__company_name']
    ordering_fields = ['price', 'created_at']
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsBusinessOwner()]
        return [permissions.AllowAny()]


# --- Product checkout -------------------------------------------------------

class CheckoutView(APIView):
    """POST /api/marketplace/checkout/ -> create an Order + Stripe Checkout session."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = CheckoutSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        v = data.validated_data

        # Resolve products; enforce one seller + one currency per order.
        resolved = []
        for row in v['items']:
            product = get_object_or_404(Product, slug=row['product'], is_active=True)
            if product.stock_status == Product.StockStatus.OUT_OF_STOCK:
                raise ValidationError(f'"{product.name}" is out of stock.')
            resolved.append((product, row['quantity']))

        companies = {p.company_id for p, _ in resolved}
        if len(companies) > 1:
            raise ValidationError('Please check out with products from one business at a time.')
        currencies = {p.currency for p, _ in resolved}
        if len(currencies) > 1:
            raise ValidationError('All items in an order must use the same currency.')

        seller = resolved[0][0].company
        currency = resolved[0][0].currency
        total = sum(p.price * q for p, q in resolved)

        with transaction.atomic():
            order = Order.objects.create(
                buyer=request.user,
                company=seller,
                currency=currency,
                total=total,
                contact_name=v['contact_name'],
                contact_email=v['contact_email'],
                shipping_address=v.get('shipping_address', ''),
                note=v.get('note', ''),
            )
            OrderItem.objects.bulk_create([
                OrderItem(order=order, product=p, name=p.name, unit_price=p.price, quantity=q)
                for p, q in resolved
            ])

        try:
            checkout_url = payments.create_order_checkout(order)
        except Exception as e:  # noqa: BLE001 — surface a clean error, drop the dangling order
            order.delete()
            raise ValidationError(f'Could not start checkout: {e}')

        return Response(
            {'checkout_url': checkout_url, 'order': OrderSerializer(order).data},
            status=status.HTTP_201_CREATED,
        )


class OrderListView(generics.ListAPIView):
    """GET /api/marketplace/orders/?role=buyer|seller"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Order.objects.select_related('company').prefetch_related('items')
        if self.request.query_params.get('role') == 'seller':
            return qs.filter(company__owner=self.request.user)
        return qs.filter(buyer=self.request.user)


class OrderDetailView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/marketplace/orders/<order_number>/
    PATCH -> seller updates fulfilment status; buyer may cancel a still-unpaid order.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'order_number'

    def get_queryset(self):
        u = self.request.user
        return (Order.objects.select_related('company').prefetch_related('items')
                .filter(buyer=u) | Order.objects.filter(company__owner=u)).distinct()

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        is_seller = order.company.owner_id == request.user.id
        is_buyer = order.buyer_id == request.user.id
        new_status = request.data.get('status')

        seller_allowed = {Order.Status.FULFILLED, Order.Status.CANCELLED, Order.Status.REFUNDED}
        if is_seller and new_status in seller_allowed:
            order.status = new_status
        elif is_buyer and new_status == Order.Status.CANCELLED and order.status == Order.Status.PENDING:
            order.status = Order.Status.CANCELLED
        else:
            raise PermissionDenied('You are not allowed to make that change.')
        order.save(update_fields=['status', 'updated_at'])
        return Response(OrderSerializer(order).data)


# --- Service booking --------------------------------------------------------

class BookingListCreateView(APIView):
    """
    GET  /api/marketplace/bookings/?role=customer|seller -> list my bookings.
    POST /api/marketplace/bookings/ -> book a service.
    Paid service -> Stripe checkout (confirmed on payment). Free service -> a
    pending request the business confirms.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = ServiceBooking.objects.select_related('company', 'service')
        if request.query_params.get('role') == 'seller':
            qs = qs.filter(company__owner=request.user)
        else:
            qs = qs.filter(customer=request.user)
        return Response(ServiceBookingSerializer(qs, many=True).data)

    def post(self, request):
        data = BookingCreateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        v = data.validated_data

        service = get_object_or_404(Service, slug=v['service'], is_active=True)
        if v['scheduled_for'] <= timezone.now():
            raise ValidationError('Please choose a date and time in the future.')

        is_paid = bool(service.price and service.price > 0)
        booking = ServiceBooking.objects.create(
            service=service,
            company=service.company,
            customer=request.user,
            service_name=service.name,
            scheduled_for=v['scheduled_for'],
            currency=service.currency,
            total=service.price or 0,
            contact_name=v['contact_name'],
            contact_email=v['contact_email'],
            note=v.get('note', ''),
            status=(ServiceBooking.Status.PENDING_PAYMENT if is_paid else ServiceBooking.Status.PENDING),
        )

        if not is_paid:
            return Response(
                {'checkout_url': None, 'booking': ServiceBookingSerializer(booking).data},
                status=status.HTTP_201_CREATED,
            )

        try:
            checkout_url = payments.create_booking_checkout(booking)
        except Exception as e:  # noqa: BLE001
            booking.delete()
            raise ValidationError(f'Could not start checkout: {e}')

        return Response(
            {'checkout_url': checkout_url, 'booking': ServiceBookingSerializer(booking).data},
            status=status.HTTP_201_CREATED,
        )


class BookingDetailView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/marketplace/bookings/<booking_number>/
    PATCH -> seller confirms/declines/completes; customer cancels.
    """
    serializer_class = ServiceBookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'booking_number'

    def get_queryset(self):
        u = self.request.user
        return (ServiceBooking.objects.select_related('company', 'service')
                .filter(customer=u) | ServiceBooking.objects.filter(company__owner=u)).distinct()

    def patch(self, request, *args, **kwargs):
        booking = self.get_object()
        is_seller = booking.company.owner_id == request.user.id
        is_customer = booking.customer_id == request.user.id
        new_status = request.data.get('status')
        S = ServiceBooking.Status

        seller_allowed = {S.CONFIRMED, S.DECLINED, S.COMPLETED, S.CANCELLED}
        if is_seller and new_status in seller_allowed:
            booking.status = new_status
        elif is_customer and new_status == S.CANCELLED and booking.status in {S.PENDING, S.CONFIRMED}:
            booking.status = S.CANCELLED
        else:
            raise PermissionDenied('You are not allowed to make that change.')
        booking.save(update_fields=['status', 'updated_at'])
        return Response(ServiceBookingSerializer(booking).data)
