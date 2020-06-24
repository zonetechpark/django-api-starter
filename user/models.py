
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
    ('CANDIDATE', 'CANDIDATE'),
    ('ADMIN', 'ADMIN'),
    ('SUPERADMIN', 'SUPERADMIN'),
)

GENDER_OPTION = (
    ('MALE', 'MALE'),
    ('FEMALE', 'FEMALE')
)

TOKEN_TYPE = (
    ('ACCOUNT_VERIFICATION', 'ACCOUNT_VERIFICATION'),
    ('PASSWORD_RESET', 'PASSWORD_RESET'),
)


def default_role():
    return ['CANDIDATE']


phone_regex = RegexValidator(
    regex=r'^\+\d{8,16}$', message="Phone number must be in international format: '+xxx...'.")


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        _('email address'), null=True, blank=True)
    password = models.CharField(max_length=255, null=True)
    firstname = models.CharField(max_length=255, blank=True, null=True)
    lastname = models.CharField(max_length=255, blank=True, null=True)
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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        ordering = ('-date_joined',)

    def __str__(self):
        return self.email


class Token(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    token_type = models.CharField(
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
