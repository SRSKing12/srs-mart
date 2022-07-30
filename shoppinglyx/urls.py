from django.contrib import admin
from django.urls import path, include
from django_email_verification import urls as email_urls
from shoppinglyx.settings import ADMIN_URL

urlpatterns = [
    path(ADMIN_URL, admin.site.urls),
    path('', include('app.urls')),
    path('email/', include(email_urls)),
]
