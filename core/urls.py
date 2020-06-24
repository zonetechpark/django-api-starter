"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="RESUMES V2 API",
        default_version='v1',
        description="mAudition Application",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="daniel.ale@zonetechpark.co"),
        license=openapi.License(name="BSD License"),
    ),
    url='https://resumes-api.toptalent.io/api/v1/',
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(r'^api/v2/api-doc(?P<format>\.json|\.yaml)$', schema_view.without_ui(
        cache_timeout=0), name='schema-json'),
    url(r'^api/v2/api-doc/$', schema_view.with_ui('swagger',
                                                  cache_timeout=0), name='schema-swagger-ui'),
    url(r'^api/v2/api-redoc/$', schema_view.with_ui('redoc',
                                                    cache_timeout=0), name='schema-redoc'),
    url(r'api/v2/accounts/', include('allauth.urls')),
    path('api/v2/api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
    # path('api/v2/auth/', include('user.urls')),
]
