from django.urls import path
from . import views

urlpatterns = [
    path('puppies/<str:pk>/', views.get_delete_update_puppy, name='puppy-detail'),
    path('puppies/', views.get_post_puppy, name='puppy'),
]