# config.py
from django.contrib import admin
from django.urls import path, include

from accounts.views import home_view, about_view, contact_us_view

urlpatterns = [
    path('', home_view, name='home'),
    path('about/', about_view, name='about'),
    path('contact-us/', contact_us_view, name='contact_us'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
]
