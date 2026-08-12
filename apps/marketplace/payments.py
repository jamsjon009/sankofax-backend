"""Stripe Checkout helpers + fulfilment for marketplace orders and service bookings.

Payments use the platform's Stripe account (mode='payment', one-time). The shared
webhook in `apps.subscriptions.views.stripe_webhook` dispatches `checkout.session.completed`
here based on `metadata.purpose` ('order' | 'booking').
"""
import stripe
from django.conf import settings
from django.utils import timezone

stripe.api_key = settings.STRIPE_SECRET_KEY


def _money(amount):
    """Decimal → integer minor units (cents)."""
    return int(round(float(amount) * 100))


def create_order_checkout(order):
    """Create a Stripe Checkout Session for a product order and return the redirect URL."""
    line_items = [{
        'price_data': {
            'currency': order.currency.lower(),
            'product_data': {'name': item.name},
            'unit_amount': _money(item.unit_price),
        },
        'quantity': item.quantity,
    } for item in order.items.all()]

    session = stripe.checkout.Session.create(
        mode='payment',
        payment_method_types=['card'],
        line_items=line_items,
        customer_email=order.contact_email,
        success_url=f'{settings.FRONTEND_URL}/dashboard/orders?success={order.order_number}',
        cancel_url=f'{settings.FRONTEND_URL}/marketplace?canceled=1',
        metadata={'purpose': 'order', 'order_id': str(order.id)},
    )
    order.stripe_session_id = session.id
    order.save(update_fields=['stripe_session_id'])
    return session.url


def create_booking_checkout(booking):
    """Create a Stripe Checkout Session for a paid service booking and return the redirect URL."""
    session = stripe.checkout.Session.create(
        mode='payment',
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': booking.currency.lower(),
                'product_data': {'name': booking.service_name},
                'unit_amount': _money(booking.total),
            },
            'quantity': 1,
        }],
        customer_email=booking.contact_email,
        success_url=f'{settings.FRONTEND_URL}/dashboard/bookings?success={booking.booking_number}',
        cancel_url=f'{settings.FRONTEND_URL}/marketplace/services?canceled=1',
        metadata={'purpose': 'booking', 'booking_id': str(booking.id)},
    )
    booking.stripe_session_id = session.id
    booking.save(update_fields=['stripe_session_id'])
    return session.url


# --- Fulfilment (called from the shared Stripe webhook) ---------------------

def fulfill_checkout(session):
    """Route a completed checkout session to the right handler by metadata.purpose."""
    purpose = (session.get('metadata') or {}).get('purpose')
    if purpose == 'order':
        _fulfill_order(session)
    elif purpose == 'booking':
        _fulfill_booking(session)


def _fulfill_order(session):
    from .models import Order
    order_id = (session.get('metadata') or {}).get('order_id')
    if not order_id:
        return
    Order.objects.filter(id=order_id, status=Order.Status.PENDING).update(
        status=Order.Status.PAID,
        paid_at=timezone.now(),
        stripe_payment_intent=session.get('payment_intent', '') or '',
    )


def _fulfill_booking(session):
    from .models import ServiceBooking
    booking_id = (session.get('metadata') or {}).get('booking_id')
    if not booking_id:
        return
    # Paid bookings are auto-confirmed once payment lands.
    ServiceBooking.objects.filter(id=booking_id, status=ServiceBooking.Status.PENDING_PAYMENT).update(
        status=ServiceBooking.Status.CONFIRMED,
        paid_at=timezone.now(),
        stripe_payment_intent=session.get('payment_intent', '') or '',
    )
