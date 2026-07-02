from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings


@receiver(pre_save, sender='directory.Listing')
def notify_listing_status_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        previous = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    if previous.listing_status == instance.listing_status:
        return

    owner_email = instance.company.owner.email
    listing_url = f"{settings.FRONTEND_URL}/listing/{instance.slug}"
    dashboard_url = f"{settings.FRONTEND_URL}/dashboard/business"

    if instance.listing_status == 'published':
        send_mail(
            subject=f'Your listing "{instance.title}" is now live!',
            message=(
                f'Great news! Your listing "{instance.title}" has been approved and is now live on SankofaX.\n\n'
                f'View it here: {listing_url}\n\n'
                f'Manage your listings: {dashboard_url}\n\n'
                '-- The SankofaX Team'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[owner_email],
            fail_silently=True,
        )

    elif instance.listing_status == 'rejected':
        reason = instance.rejection_reason or 'Please review our community guidelines and resubmit.'
        send_mail(
            subject=f'Update on your listing "{instance.title}"',
            message=(
                f'Thank you for submitting "{instance.title}" to SankofaX.\n\n'
                f'Unfortunately, we were unable to approve this listing at this time.\n\n'
                f'Reason: {reason}\n\n'
                f'You can edit and resubmit your listing here: {dashboard_url}\n\n'
                f'If you have questions, reply to this email.\n\n'
                '-- The SankofaX Team'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[owner_email],
            fail_silently=True,
        )
