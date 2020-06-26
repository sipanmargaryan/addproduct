import secrets

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone

from core.models import City
from core.utils import get_file_path, get_image_from_url

__all__ = (
    'User',
    'Notification',
    'SocialConnection',
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=16, unique=True, null=True)
    avatar = models.ImageField(upload_to=get_file_path, blank=True)
    device_id = models.CharField(max_length=200, editable=False, null=True)
    email_confirmation_token = models.CharField(max_length=64, editable=False, null=True)
    reset_password_token = models.CharField(max_length=64, editable=False, null=True)
    reset_password_request_date = models.DateTimeField(null=True)

    city = models.ForeignKey(City, null=True, on_delete=models.CASCADE)

    username = None

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def generate_password_request_date(self):
        self.reset_password_request_date = timezone.now()

    def get_avatar(self) -> str:
        if self.avatar:
            return self.avatar.url

    def set_avatar(self, avatar_url: str):
        """
        Download image based on url an attach to user if valid.
        :param avatar_url:
        :return:
        """
        if not avatar_url:
            return

        file = get_image_from_url(avatar_url)
        if not file:
            return

        filename = avatar_url.split('/')[-1]
        if not any(filter(lambda ext: ext in filename, ['.jpeg', '.jpg', '.png'])):
            filename = 'avatar.jpeg'

        filename = get_file_path(self, filename)
        self.avatar.save(filename, file, save=True)

    def get_seller_url(self):
        return reverse_lazy('ads:seller', kwargs={'user': self.pk})

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe()


class Notification(models.Model):
    ad_answer = models.BooleanField(default=True)
    news_offer_promotion = models.BooleanField(default=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)


class SocialConnection(models.Model):
    GOOGLE = 'google'
    FACEBOOK = 'facebook'
    TWITTER = 'twitter'
    INSTAGRAM = 'instagram'

    PROVIDERS = (
        (GOOGLE, 'Google'),
        (FACEBOOK, 'Facebook'),
        (TWITTER, 'Twitter'),
        (INSTAGRAM, 'Instagram'),
    )

    provider = models.CharField(max_length=16, choices=PROVIDERS)
    provider_id = models.CharField(max_length=32, unique=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('provider', 'user'), )

    @classmethod
    def providers(cls) -> list:
        return [provider[0] for provider in cls.PROVIDERS]
