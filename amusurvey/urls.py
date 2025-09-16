# amusurvey/urls.py

from django.contrib import admin
from django.urls import path, include
from users.views import home  # <-- IMPORTANT: We import YOUR home view.

urlpatterns = [
    path('admin/', admin.site.urls),

    # This is the REAL home page of your site. It uses your 'home' view.
    path('', home, name='home'),

    # This handles login/logout at /accounts/...
    path('accounts/', include('users.urls')),

    # This says that all survey-related pages (the dashboard, create, detail, etc.)
    # will start with /surveys/.
    path('surveys/', include('surveys.urls')),
]