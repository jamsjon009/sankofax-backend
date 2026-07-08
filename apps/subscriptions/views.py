import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Plan, Subscription
from .serializers import PlanSerializer, SubscriptionSerializer, CheckoutSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


class PlanListView(generics.ListAPIView):
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # plain array, plans are few

    def get_queryset(self):
        qs = Plan.objects.filter(is_active=True)
        region = self.request.query_params.get('region') or getattr(self.request.user, 'region', None)
        if region:
            qs = qs.filter(region__in=[region, ''])
        return qs


class SubscriptionListView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)


class MySubscriptionView(generics.RetrieveAPIView):
    """Active subscription for the current user, with listing usage count."""
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(
            Subscription,
            user=self.request.user,
            status__in=[Subscription.Status.ACTIVE, Subscription.Status.TRIALING, Subscription.Status.PAST_DUE],
        )

    def retrieve(self, request, *args, **kwargs):
        from apps.directory.models import Listing
        try:
            instance = self.get_object()
        except Exception:
            return Response(None, status=204)
        data = self.get_serializer(instance).data
        data['listings_used'] = Listing.objects.filter(
            company__owner=request.user,
            listing_status__in=['published', 'pending_review', 'draft'],
        ).count()
        return Response(data)


class BillingPortalView(APIView):
    """Create a Stripe customer portal session and return the URL."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        sub = Subscription.objects.filter(
            user=request.user,
            status__in=[Subscription.Status.ACTIVE, Subscription.Status.TRIALING],
        ).first()

        if not sub or not sub.stripe_customer_id:
            return Response({'error': 'No active subscription found.'}, status=400)

        session = stripe.billing_portal.Session.create(
            customer=sub.stripe_customer_id,
            return_url=f'{settings.FRONTEND_URL}/dashboard/billing',
        )
        return Response({'url': session.url})


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = Plan.objects.get(pk=serializer.validated_data['plan_id'])

        if not plan.stripe_price_id:
            return Response({'error': 'Plan not available for online checkout.'}, status=400)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price': plan.stripe_price_id, 'quantity': 1}],
            mode='subscription' if plan.billing_cycle != 'one_time' else 'payment',
            success_url=f'{settings.FRONTEND_URL}/dashboard/billing?success=1',
            cancel_url=f'{settings.FRONTEND_URL}/pricing',
            metadata={
                'user_id': str(request.user.id),
                'plan_id': str(plan.id),
                'company_id': str(serializer.validated_data.get('company_id', '')),
            },
        )
        return Response({'checkout_url': session.url})


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        _handle_checkout_complete(session)

    return HttpResponse(status=200)


def _handle_checkout_complete(session):
    from apps.accounts.models import User
    user_id = session['metadata'].get('user_id')
    plan_id = session['metadata'].get('plan_id')
    company_id = session['metadata'].get('company_id') or None

    try:
        user = User.objects.get(pk=user_id)
        plan = Plan.objects.get(pk=plan_id)
        Subscription.objects.create(
            user=user,
            plan=plan,
            company_id=company_id if company_id else None,
            stripe_subscription_id=session.get('subscription', ''),
            stripe_customer_id=session.get('customer', ''),
            status=Subscription.Status.ACTIVE,
        )
        if not user.is_business_owner:
            from apps.accounts.models import User as U
            U.objects.filter(pk=user.pk).update(role='business_owner')
    except Exception:
        pass
