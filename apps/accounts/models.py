import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'super_admin')
        extra_fields.setdefault('is_verified', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        VISITOR = 'visitor', 'Visitor'
        BUSINESS_OWNER = 'business_owner', 'Business Owner'
        MODERATOR = 'moderator', 'Moderator'
        STAFF = 'staff', 'Staff'
        ADMIN = 'admin', 'Admin'
        SUPER_ADMIN = 'super_admin', 'Super Admin'

    class Region(models.TextChoices):
        GLOBAL_NORTH = 'global_north', 'Global North'
        GLOBAL_SOUTH = 'global_south', 'Global South'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VISITOR)
    is_verified = models.BooleanField(default=False)
    region = models.CharField(max_length=20, choices=Region.choices, default=Region.GLOBAL_NORTH)
    country = models.CharField(max_length=2, blank=True, help_text='ISO 3166-1 alpha-2 country code')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    @property
    def is_business_owner(self):
        return self.role in [self.Role.BUSINESS_OWNER, self.Role.ADMIN, self.Role.SUPER_ADMIN]

    @property
    def is_admin_or_staff(self):
        return self.role in [
            self.Role.STAFF, self.Role.MODERATOR, self.Role.ADMIN, self.Role.SUPER_ADMIN
        ] or self.is_staff

    @property
    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN or self.is_superuser


class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification_token')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return (timezone.now() - self.created_at).total_seconds() > 86400  # 24 hours

    def __str__(self):
        return f'Verification token for {self.user.email}'


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_expired(self):
        return (timezone.now() - self.created_at).total_seconds() > 3600  # 1 hour

    def __str__(self):
        return f'Reset token for {self.user.email}'


# Proxy models for admin panel segmentation

class AdminUserProxy(User):
    class Meta:
        proxy = True
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'


class CompanyUserProxy(User):
    class Meta:
        proxy = True
        verbose_name = 'Company Account'
        verbose_name_plural = 'Company Accounts'


class RegularUserProxy(User):
    class Meta:
        proxy = True
        verbose_name = 'General User'
        verbose_name_plural = 'General Users'