"""Stripe Checkout + fulfilment for story-promotion purchases.

Uses the platform Stripe account (mode='payment'). The shared webhook in
`apps.subscriptions.views.stripe_webhook` dispatches here when
`metadata.purpose == 'story'`.
"""
import stripe
from django.conf import settings
from django.utils import timezone

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_submission_checkout(submission):
    """Create a Stripe Checkout Session for a story submission and return the redirect URL."""
    session = stripe.checkout.Session.create(
        mode='payment',
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': submission.currency.lower(),
                'product_data': {'name': f'{submission.package.name} — {submission.company.company_name}'},
                'unit_amount': int(round(float(submission.amount) * 100)),
            },
            'quantity': 1,
        }],
        customer_email=submission.contact_email,
        success_url=f'{settings.FRONTEND_URL}/dashboard/promotions?success={submission.reference}',
        cancel_url=f'{settings.FRONTEND_URL}/promote?canceled=1',
        metadata={'purpose': 'story', 'submission_id': str(submission.id)},
    )
    submission.stripe_session_id = session.id
    submission.save(update_fields=['stripe_session_id'])
    return session.url


def fulfill_checkout(session):
    """Mark a story submission paid → moves it into the admin review queue."""
    from .models import StorySubmission
    submission_id = (session.get('metadata') or {}).get('submission_id')
    if not submission_id:
        return
    StorySubmission.objects.filter(
        id=submission_id, status=StorySubmission.Status.PENDING_PAYMENT,
    ).update(
        status=StorySubmission.Status.IN_REVIEW,
        paid_at=timezone.now(),
        stripe_payment_intent=session.get('payment_intent', '') or '',
    )
