from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("secret-panel/", admin.site.urls),
]
