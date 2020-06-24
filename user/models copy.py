
from django.core.files import File
from urllib.request import urlretrieve
import uuid
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser
from datetime import datetime, timedelta, timezone
from django.contrib.auth.models import PermissionsMixin
from django.conf import settings
from django.urls import reverse
from django.contrib.postgres.fields import ArrayField
from .managers import CustomUserManager
from django.core.exceptions import ValidationError


USER_ROLE = (
    ('VIEWER', 'VIEWER'),
    ('TALENT', 'TALENT'),
    ('SCOUT', 'SCOUT'),
    ('JUDGE', 'JUDGE'),
    ('BRAND', 'BRAND'),
    ('ADMIN', 'ADMIN'),
    ('SUPERADMIN', 'SUPERADMIN'),
)

AUTH_TYPE = (
    ('email', 'email'),
    ('phone', 'phone'),
    ('gmail', 'gmail'),
    ('facebook', 'facebook')
)

GENDER_OPTION = (
    ('Male', 'Male'),
    ('Female', 'Female')
)

TOKEN_TYPE = (
    ('ACCOUNT_VERIFICATION', 'ACCOUNT_VERIFICATION'),
    ('PASSWORD_RESET', 'PASSWORD_RESET'),
)


def default_role():
    return ['TALENT']


phone_regex = RegexValidator(
    regex=r'^\+\d{8,16}$', message="Phone number must be in international format: '+xxx...'.")


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auth_type = models.CharField(
        max_length=20, choices=AUTH_TYPE, default='email')
    username = models.CharField(max_length=100, unique=True)
    old_id = models.CharField(
        max_length=100, blank=True, null=True)
    old_image = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(
        _('email address'), null=True, blank=True)
    password = models.CharField(max_length=255, null=True)
    fullname = models.CharField(max_length=255, blank=True, null=True)
    image = models.FileField(upload_to='users/', blank=True, null=True)
    phone = models.CharField(
        validators=[phone_regex], max_length=17, blank=True, null=True)
    roles = ArrayField(models.CharField(max_length=20, blank=True,
                                        choices=USER_ROLE), default=default_role, size=4)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True)
    verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        ordering = ('-date_joined',)

    def __str__(self):
        return self.username

    def create_image_from_url(self, avatar_url):
        try:
            name, _ = urlretrieve(avatar_url)
            name = f"{name}"
            self.image.save(name, File(open(name, 'rb')))
        except Exception as e:
            self.is_active = False
            self.save(update_fields=['is_active'])


class Token(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    type = models.CharField(
        max_length=100, choices=TOKEN_TYPE, default='ACCOUNT_VERIFICATION')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token

    def is_valid(self):
        lifespan_in_seconds = float(settings.TOKEN_LIFESPAN * 60 * 60)
        now = datetime.now(timezone.utc)
        time_diff = now - self.created_at
        time_diff = time_diff.total_seconds()
        if time_diff >= lifespan_in_seconds:
            return False
        return True

    def verify_user(self):
        self.user.verified = True
        self.user.save()


class TempUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(
        validators=[phone_regex], max_length=17, blank=True, null=True)
    auth_type = models.CharField(
        max_length=20, choices=AUTH_TYPE, default='email')
    token = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.token

    def is_valid(self):
        lifespan_in_seconds = float(settings.TOKEN_LIFESPAN * 60)
        now = datetime.now()
        time_diff = now - self.created_at
        time_diff = time_diff.total_seconds()
        if time_diff >= lifespan_in_seconds:
            return False
        return True


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='user_profile')
    gender = models.CharField(
        max_length=10, choices=GENDER_OPTION, null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    date_of_birth = models.DateTimeField(null=True, blank=True)
    eye_color = models.CharField(max_length=100, null=True, blank=True)
    skin_color = models.CharField(max_length=100, null=True, blank=True)
    biography = models.TextField(null=True, blank=True)
    website = models.CharField(max_length=200, null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return self.user.email


class UserDevice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.CharField(max_length=255)
    registration_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return self.device


class Follow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='follow_authors')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following_users')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created_at',)
        unique_together = [['author', 'user']]

    def __str__(self):
        return self.user.email
