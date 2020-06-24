import os
import asyncio
from django.core.files import File
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, exceptions
from django.utils.crypto import get_random_string
from django.db import IntegrityError
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from datetime import date
from dateutil.relativedelta import relativedelta
from email_validator import validate_email, EmailNotValidError
from .models import Token


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'firstname', 'lastname', 'email', 'role', 'image']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user object"""

    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'password', 'firstname', 'lastname',
                  'phone', 'image', 'roles', 'date_joined')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8},
                        'date_joined': {'read_only': True}}

    def validate(self, attrs):
        email = attrs['email'].lower().strip()
        if get_user_model().objects.filter(email=email).exists():
            raise serializers.ValidationError('Email already exists')
        try:
            valid = validate_email(attrs['email'])
            attrs['email'] = valid.email
            return super().validate(attrs)
        except EmailNotValidError as e:
            raise serializers.ValidationError(e)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance = super().update(instance, validated_data)
        if validated_data.get('password', False):
            instance.set_password(validated_data.get('password'))
            instance.save()
        return instance


class CustomObtainTokenPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        if not user.verified:
            raise exceptions.AuthenticationFailed(
                _('Account not yet verified.'), code='authentication')
        token = super().get_token(user)
        # Add custom claims
        token.id = user.id
        token['email'] = user.email
        token['roles'] = user.roles
        token['fullname'] = user.firstname + ' ' + user.lastname
        if user.image:
            token['image'] = user.image.url
        token['phone'] = user.phone
        return token


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        if email:
            user = authenticate(
                request=self.context.get('request'),
                username=email.lower().strip(),
                password=password
            )

        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')
        attrs['user'] = user
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset"""
    email = serializers.CharField()

    def create(self, validated_data):
        email = validated_data.get('email', None)
        user = get_user_model().objects.filter(email=email, is_active=True).first()
        if not user:
            msg = _('Invalid email provided')
            raise serializers.ValidationError(msg, code='authentication')
        token = Token.objects.create(
            user=user, type='PASSWORD_RESET', token=get_random_string(length=6))
        email_data = {'fullname': user.firstname, 'email': user.email,
                      'token': token.token}
        # send_password_reset_email.delay(email_data)
        return token


class PasswordResetVerifySerializer(serializers.Serializer):
    """Serializer for password reset token verification"""
    token = serializers.CharField()

    def create(self, validated_data):
        token = validated_data.get('token', None)
        token_data = Token.objects.filter(token=token).first()
        if not token_data:
            msg = _('Invalid token provided')
            raise serializers.ValidationError(msg, code='authentication')
        return token_data


class PasswordResetChangeSerializer(serializers.Serializer):
    """Serializer for password change on reset"""
    token = serializers.CharField()
    new_password = serializers.CharField()

    def create(self, validated_data):
        token = validated_data.get('token', None)
        new_password = validated_data.get('new_password', None)
        token_data = Token.objects.filter(token=token).first()
        if not token_data:
            msg = _('Invalid token provided')
            raise serializers.ValidationError(msg, code='authentication')
        token_data.user.set_password(new_password)
        token_data.user.save()
        token_data.delete()
        return token_data


class RegisterVerifySerializer(serializers.Serializer):
    """Serializer for registration verification object"""
    token = serializers.CharField()
