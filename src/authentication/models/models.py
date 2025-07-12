from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from authentication.models.managers import CustomUserManager
from core.models import Society


class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_ADMIN = 'ADMIN'
    USER_TYPE_PARENT = 'PARENT'
    USER_TYPE_INSTRUCTOR = 'INSTRUCTOR'

    USER_TYPE_CHOICES = [
        (USER_TYPE_ADMIN, USER_TYPE_ADMIN),
        (USER_TYPE_PARENT, USER_TYPE_PARENT),
        (USER_TYPE_INSTRUCTOR, USER_TYPE_INSTRUCTOR),
    ]

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=False, null=False)
    full_name = models.CharField(max_length=63, blank=False, null=False)
    # TODO(AbhilakshSinghReen): add this in later
    # display_image = models.ImageField(upload_to='user_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    user_type = models.CharField(max_length=31, choices=USER_TYPE_CHOICES, null=False, blank=False)

    last_sent_email_otp = models.CharField(max_length=7, blank=False, null=False)
    last_sent_email_otp_expiration = models.DateTimeField(auto_now_add=True)
    last_sent_email_otp_used = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'full_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = "Base User"
        verbose_name_plural = "Base Users"


class ParentUser(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='parent_user')
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='parent_society')
    house_number = models.CharField(max_length=31)

    class Meta:
        verbose_name = "Parent User"
        verbose_name_plural = "Parent Users"


class InstructorUser(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='instructor_user')
    address = models.TextField()

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = "Instructor User"
        verbose_name_plural = "Instructor Users"
