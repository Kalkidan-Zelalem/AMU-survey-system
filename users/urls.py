# users/urls.py - NEW AND CORRECTED CODE

from django.urls import path, include
from .views import register

urlpatterns = [
    # Our custom registration page URL
    path('register/', register, name='register'),
    
    # This INCLUDES all of Django's built-in URLs
    # for login, logout, and password resets.
    path('', include('django.contrib.auth.urls')),
]