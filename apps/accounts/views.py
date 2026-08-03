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
        kwargs['partial'] = True
        instance = self.get_object()

        # Handle avatar upload + resize
        if 'avatar' in request.FILES:
            avatar_file = request.FILES['avatar']
            try:
                from PIL import Image as PILImage
                import io
                from django.core.files.uploadedfile import InMemoryUploadedFile

                img = PILImage.open(avatar_file)
                img = img.convert('RGB')
                max_size = (400, 400)
                img.thumbnail(max_size, PILImage.LANCZOS)

                output = io.BytesIO()
                img.save(output, format='JPEG', quality=85)
                output.seek(0)

                filename = f"avatar_{instance.id}.jpg"
                request.FILES['avatar'] = InMemoryUploadedFile(
                    output, 'ImageField', filename,
                    'image/jpeg', output.getbuffer().nbytes, None
                )
            except Exception:
                pass  # Pillow not available or error — save original

        return super().update(request, *args, **kwargs)


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