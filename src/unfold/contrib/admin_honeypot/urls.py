from . import views
from django.urls import path

app_name="unfold.contrib.admin_honeypot"

urlpatterns = [
    path('login/', views.AdminHoneypot.as_view(), name='login'),
    path('', views.AdminHoneypot.as_view(), name='index'),
]