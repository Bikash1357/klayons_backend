from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        is_superuser = extra_fields.get('is_superuser', False)

        # For regular users, require OTP
        if not is_superuser:
            if not extra_fields.get('last_sent_email_otp'):
                raise ValueError('Regular users must have an OTP.')
        else:
            # For superusers, password is mandatory
            if not password:
                raise ValueError('Superusers must have a password.')

        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password=password, **extra_fields)
