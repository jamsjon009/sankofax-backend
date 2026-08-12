from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(user, token):
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    html = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:0 auto;padding:32px 24px;">
      <h2 style="color:#1c1a17;margin-bottom:8px;">Verify your SankofaX account</h2>
      <p style="color:#7a6a56;margin-bottom:24px;">Click the button below to verify your email address and activate your account.</p>
      <a href="{verify_url}" style="display:inline-block;background:#b5813b;color:#fff;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:600;">
        Verify Email
      </a>
      <p style="color:#7a6a56;font-size:13px;margin-top:24px;">This link expires in 24 hours. If you did not create an account, ignore this email.</p>
      <hr style="border:none;border-top:1px solid #e8ddd0;margin:24px 0;">
      <p style="color:#b5813b;font-size:13px;font-weight:600;">SankofaX &mdash; Global Business Directory</p>
    </div>
    """
    send_mail(
        subject='Verify your SankofaX account',
        message=f'Verify your account: {verify_url}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html,
        fail_silently=True,
    )


def send_password_reset_email(user, token):
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    html = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:0 auto;padding:32px 24px;">
      <h2 style="color:#1c1a17;margin-bottom:8px;">Reset your password</h2>
      <p style="color:#7a6a56;margin-bottom:24px;">We received a request to reset the password for your SankofaX account.</p>
      <a href="{reset_url}" style="display:inline-block;background:#b5813b;color:#fff;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:600;">
        Reset Password
      </a>
      <p style="color:#7a6a56;font-size:13px;margin-top:24px;">This link expires in 1 hour. If you did not request a reset, ignore this email.</p>
      <hr style="border:none;border-top:1px solid #e8ddd0;margin:24px 0;">
      <p style="color:#b5813b;font-size:13px;font-weight:600;">SankofaX &mdash; Global Business Directory</p>
    </div>
    """
    send_mail(
        subject='Reset your SankofaX password',
        message=f'Reset your password: {reset_url}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html,
        fail_silently=True,
    )