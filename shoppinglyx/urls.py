from django.contrib import admin
from django.urls import path, include
from django_email_verification import urls as email_urls
from shoppinglyx.settings import ADMIN_URL
from django.urls.conf import re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path(ADMIN_URL, admin.site.urls),
    path('', include('app.urls')),
    path('email/', include(email_urls)),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
