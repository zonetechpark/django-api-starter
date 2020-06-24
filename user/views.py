import asyncio
from django.conf import settings
from rest_framework.decorators import action
from rest_framework import filters, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth import get_user_model, logout
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.authtoken.views import ObtainAuthToken
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from user.models import User, Token, TempUser, Follow, Profile
from user.permissions import IsAdmin
from .serializers import (UserSerializer, RegisterVerifySerializer, AuthTokenSerializer, CustomObtainTokenPairSerializer,
                          PasswordResetChangeSerializer, PasswordResetSerializer, PasswordResetVerifySerializer)


class UserViewsets(viewsets.ModelViewSet):
    """Register new user"""
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['email', 'firstname', 'lastname', 'phone']

    def get_serializer_class(self):
        if self.action == 'verify':
            return RegisterVerifySerializer
        elif self.action == 'verify_resend' or self.action == 'reset_password':
            return PasswordResetSerializer
        elif self.action == 'reset_password_change':
            return PasswordResetChangeSerializer
        elif self.action == 'reset_password_token_validate':
            return PasswordResetVerifySerializer
        return super().get_serializer_class()

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action in ['createuser', 'verify', 'verify_resend', 'reset_password', 'reset_password_token_validate', 'retrieve', 'list']:
            permission_classes = [AllowAny]
        elif self.action in ['destroy', 'partial_update']:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_response_data(self, paginated_queryset):
        serializer = self.serializer_class(paginated_queryset, many=True)
        return serializer.data

    @action(methods=['POST'], detail=False, url_path='register/verification')
    def verify(self, request):
        """This endpoint verifies user account on company registration"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            token = Token.objects.filter(
                token=serializer.validated_data.get('token')).first()
            if token and token.is_valid():
                token.verify_user()
                token.delete()
                return Response({'success': True}, status=status.HTTP_200_OK)
            return Response({'message': 'Invalid token'}, status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=False, url_path='register/verification/resend')
    def verify_resend(self, request):
        """This endpoint resend company registration verification email"""
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid():
                user = User.objects.filter(
                    email=serializer.validated_data.get('email')).first()
                if user:
                    token = Token.objects.create(
                        user=user, type='ACCOUNT_VERIFICATION', token=get_random_string(length=100))
                    email_data = {'fullname': user.firstname, 'email': user.email,
                                  'token': token.token}
                    # send_registration_email.delay(email_data)
                    return Response({'success': True}, status=status.HTTP_200_OK)
                return Response({'message': 'Invalid email'}, status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['POST'], detail=False)
    def reset_password(self, request):
        """This endpoint initiates Password reset"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=False, url_path='reset_password/change')
    def reset_password_change(self, request):
        """Change user password after password reset has been initiated."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=False, url_path='reset_password/validate_token')
    def reset_password_token_validate(self, request):
        """Validate password reset token"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=False, filter_backends=[], permission_classes=[IsAuthenticated], url_path='logout')
    def logout(self, request, pk=None):
        """Endpoint to logout"""
        logout(request)
        return Response(status=status.HTTP_200_OK)


class CustomObtainTokenPairView(TokenObtainPairView):
    """Login with any of phone, email or username"""
    serializer_class = CustomObtainTokenPairSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        try:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'created': created,
                'roles': user.roles
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
