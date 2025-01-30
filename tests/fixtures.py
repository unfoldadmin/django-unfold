import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from unfold.admin import ModelAdmin
from unfold.sites import UnfoldAdminSite

User = get_user_model()


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username="admin", email="admin@example.com", password="password"
    )


@pytest.fixture
def admin_request(admin_user):
    request = RequestFactory().get("/")
    request.user = admin_user
    return request


@pytest.fixture
def user_model_admin():
    return ModelAdmin(model=User, admin_site=UnfoldAdminSite())


@pytest.fixture
def user_changelist(admin_request, user_model_admin):
    return user_model_admin.get_changelist_instance(admin_request)
