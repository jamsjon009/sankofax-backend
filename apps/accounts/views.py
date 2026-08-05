from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    country_from_request, country_to_region,
)
from .models import EmailVerificationToken, PasswordResetToken
from .emails import send_verification_email, send_password_reset_email

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Send verification email
        token_obj, _ = EmailVerificationToken.objects.get_or_create(user=user)
        send_verification_email(user, token_obj.token)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


class RegionView(APIView):
    """Detect the visitor's region from geo headers so pricing can default to
    the right tier automatically. Returns blank values when undetectable
    (e.g. local dev) — the client keeps its own default in that case."""
    permission_classes = [AllowAny]

    def get(self, request):
        country = country_from_request(request)
        return Response({
            'country': country,
            'region': country_to_region(country) if country else '',
        })


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data['refresh'])
            token.blacklist()
        except Exception:
            pass
        return Response({'detail': 'Logged out.'}, status=status.HTTP_205_RESET_CONTENT)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [
        __import__('rest_framework.parsers', fromlist=['MultiPartParser']).MultiPartParser,
        __import__('rest_framework.parsers', fromlist=['JSONParser']).JSONParser,
    ]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Handle the avatar ourselves (resize + re-encode to JPEG) and save it
        # directly on the instance. Doing this outside the serializer avoids a
        # DRF pitfall: reading the uploaded stream here and then swapping
        # request.FILES doesn't reliably reach the serializer's cached
        # request.data, which previously left small in-memory uploads (PNGs,
        # screenshots) looking "corrupted" and failing validation.
        avatar_file = request.FILES.get('avatar')
        if avatar_file is not None:
            instance.avatar = self._process_avatar(avatar_file, instance)
            instance.save(update_fields=['avatar'])

        # Update any remaining writable fields (skip avatar — already handled).
        data = {k: v for k, v in request.data.items() if k != 'avatar'}
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self.get_serializer(instance).data)

    @staticmethod
    def _process_avatar(avatar_file, instance):
        """Validate, resize (max 400x400) and re-encode the avatar to JPEG.

        Returns a ContentFile ready to assign to instance.avatar. Raises a DRF
        ValidationError with a clear message on oversize or unsupported files.
        """
        from rest_framework.exceptions import ValidationError
        from django.conf import settings
        import io

        max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 10 * 1024 * 1024)
        if getattr(avatar_file, 'size', 0) > max_size:
            mb = max_size // (1024 * 1024)
            raise ValidationError({'avatar': [f'Image is too large. Please upload a file under {mb}MB.']})

        try:
            from PIL import Image as PILImage
            from django.core.files.base import ContentFile

            avatar_file.seek(0)
            img = PILImage.open(avatar_file)
            img = img.convert('RGB')
            resample = getattr(getattr(PILImage, 'Resampling', PILImage), 'LANCZOS')
            img.thumbnail((400, 400), resample)

            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85)
            return ContentFile(output.getvalue(), name=f'avatar_{instance.id}.jpg')
        except ValidationError:
            raise
        except Exception:
            raise ValidationError(
                {'avatar': ['That file is not a supported image. Please upload a JPG, PNG or WebP.']}
            )


class UpgradeToBusinessView(APIView):
    """Upgrade the current visitor to a Business Owner.

    Free role flip so a visitor can start listing a business. Idempotent —
    users who are already business owners (or admins/staff) just get their
    current profile back. Higher roles (staff/admin/super_admin) are never
    downgraded.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role == User.Role.VISITOR:
            user.role = User.Role.BUSINESS_OWNER
            user.save(update_fields=['role'])
        return Response(UserSerializer(user).data)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'detail': 'Token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token_obj = EmailVerificationToken.objects.select_related('user').get(token=token)
        except EmailVerificationToken.DoesNotExist:
            return Response({'detail': 'Invalid verification link.'}, status=status.HTTP_400_BAD_REQUEST)

        if token_obj.is_expired():
            return Response({'detail': 'Verification link has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

        user = token_obj.user
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        token_obj.delete()

        return Response({'detail': 'Email verified successfully. You can now sign in.'})


class ResendVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal whether email exists
            return Response({'detail': 'If that email is registered, a verification link has been sent.'})

        if user.is_verified:
            return Response({'detail': 'This account is already verified.'})

        token_obj, _ = EmailVerificationToken.objects.get_or_create(user=user)
        # Refresh token if expired
        if token_obj.is_expired():
            token_obj.delete()
            token_obj = EmailVerificationToken.objects.create(user=user)

        send_verification_email(user, token_obj.token)
        return Response({'detail': 'If that email is registered, a verification link has been sent.'})


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            # Invalidate old tokens
            user.password_reset_tokens.filter(used=False).update(used=True)
            token_obj = PasswordResetToken.objects.create(user=user)
            send_password_reset_email(user, token_obj.token)
        except User.DoesNotExist:
            pass  # Don't reveal whether email exists

        return Response({'detail': 'If that email is registered, a password reset link has been sent.'})


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token_obj = PasswordResetToken.objects.select_related('user').get(
                token=serializer.validated_data['token'],
                used=False,
            )
        except PasswordResetToken.DoesNotExist:
            return Response({'detail': 'Invalid or expired reset link.'}, status=status.HTTP_400_BAD_REQUEST)

        if token_obj.is_expired():
            return Response({'detail': 'Reset link has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

        user = token_obj.user
        user.set_password(serializer.validated_data['password'])
        user.save(update_fields=['password'])
        token_obj.used = True
        token_obj.save(update_fields=['used'])

        return Response({'detail': 'Password reset successfully. You can now sign in.'})