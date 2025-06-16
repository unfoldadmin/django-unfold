import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import RequestFactory
from django.utils.timezone import now

from unfold.admin import ModelAdmin
from unfold.sites import UnfoldAdminSite

User = get_user_model()


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username="admin@example.com",
        email="admin@example.com",
        password="password",
        date_joined=now(),
    )


@pytest.fixture
def staff_user():
    view_user_permission = Permission.objects.get(codename="view_user")
    change_user_permission = Permission.objects.get(codename="change_user")
    view_actionuser_permission = Permission.objects.get(codename="view_actionuser")
    change_actionuser_permission = Permission.objects.get(codename="change_actionuser")

    user = User.objects.create_user(
        username="staff@example.com",
        email="staff@example.com",
        password="password",
        date_joined=now(),
    )
    user.is_staff = True
    user.save()
    user.user_permissions.add(view_user_permission)
    user.user_permissions.add(change_user_permission)
    user.user_permissions.add(view_actionuser_permission)
    user.user_permissions.add(change_actionuser_permission)
    return user


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
