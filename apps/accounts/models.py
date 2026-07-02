import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


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
        extra_fields.setdefault('role', User.Role.ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        VISITOR = 'visitor', 'Visitor'
        BUSINESS_OWNER = 'business_owner', 'Business Owner'
        STAFF = 'staff', 'Staff'
        ADMIN = 'admin', 'Admin'

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
        return self.role in [self.Role.BUSINESS_OWNER, self.Role.ADMIN]

    @property
    def is_admin_or_staff(self):
        return self.role in [self.Role.STAFF, self.Role.ADMIN] or self.is_staff
