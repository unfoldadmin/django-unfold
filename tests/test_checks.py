import pytest
from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.checks import Tags, run_checks
from django.db import OperationalError

from unfold.admin import ModelAdmin
from unfold.checks import UnfoldModelAdminChecks
from unfold.decorators import action

User = get_user_model()


@pytest.mark.django_db
def test_run_all_checks():
    app_config = apps.get_app_config("example")

    errors = run_checks(
        app_configs=[app_config],
        tags=[Tags.admin],
    )

    assert errors == []


@pytest.mark.django_db
def test_actions_exception_action_has_wrong_permission_method():
    admin.site.unregister(User)

    @admin.register(User)
    class SampleModelAdmin(ModelAdmin):
        actions_list = ["action_with_wrong_permission_name"]

        @action(permissions=["wrong_permission"])
        def action_with_wrong_permission_name(self, request):
            return

    app_config = apps.get_app_config("example")

    errors = run_checks(
        app_configs=[app_config],
        tags=[Tags.admin],
    )

    assert len(errors) == 1

    assert (
        errors[0].msg
        == "SampleModelAdmin must define a has_wrong_permission_permission() method for the action_with_wrong_permission_name() action."
    )


@pytest.mark.django_db
def test_actions_exception_action_has_wrong_djang_permission():
    admin.site.unregister(User)

    @admin.register(User)
    class SampleModelAdmin(ModelAdmin):
        actions_list = ["action_with_wrong_permission_name"]

        @action(permissions=["some_app.non_existing_permission"])
        def action_with_wrong_permission_name(self, request):
            return

    app_config = apps.get_app_config("example")

    errors = run_checks(
        app_configs=[app_config],
        tags=[Tags.admin],
    )

    assert len(errors) == 1
    assert (
        errors[0].msg
        == "@action decorator on action_with_wrong_permission_name() in class SampleModelAdmin specifies permission some_app.non_existing_permission which does not exists."
    )


def test_actions_exception_database_not_ready(monkeypatch):
    class SampleModelAdmin(ModelAdmin):
        actions_list = ["action_with_permission"]

        @action(permissions=["some_app.some_permission"])
        def action_with_permission(self, request):
            return

    class UnavailableQuerySet:
        def exists(self):
            raise OperationalError

    monkeypatch.setattr(
        "unfold.checks.Permission.objects.filter",
        lambda *args, **kwargs: UnavailableQuerySet(),
    )

    errors = UnfoldModelAdminChecks()._check_unfold_action_permission_methods(
        SampleModelAdmin(User, admin.site)
    )

    assert len(errors) == 1
    assert errors[0].id == "admin.W129"
    assert (
        errors[0].msg
        == "Could not check for @action decorator permission some_app.some_permission on action_with_permission() in class SampleModelAdmin existence because the database is not ready yet."
    )
