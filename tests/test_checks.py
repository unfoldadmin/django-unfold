import pytest
from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.checks import Tags, run_checks
from example.models import Invoice, TagUserNote

from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.decorators import action

User = get_user_model()


@pytest.fixture(autouse=True)
def restore_admin_registry():
    """These tests replace the admin of User, put the original one back."""
    original = admin.site._registry.copy()
    yield
    admin.site._registry = original


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


@pytest.mark.django_db
def test_nested_inlines_self_referencing_chain_without_max_depth():
    admin.site.unregister(User)

    class SelfReferencingInline(TabularInline):
        model = Invoice

    SelfReferencingInline.inlines = [SelfReferencingInline]

    @admin.register(User)
    class SampleModelAdmin(ModelAdmin):
        inlines = [SelfReferencingInline]

    errors = run_checks(
        app_configs=[apps.get_app_config("example")],
        tags=[Tags.admin],
    )

    assert len(errors) == 1
    assert errors[0].id == "unfold.E001"
    assert (
        errors[0].msg == "SampleModelAdmin declares nested inlines which contain "
        "themselves (SelfReferencingInline -> SelfReferencingInline)."
    )


@pytest.mark.django_db
def test_nested_inlines_self_referencing_chain_with_max_depth():
    admin.site.unregister(User)

    class SelfReferencingInline(TabularInline):
        model = Invoice

    SelfReferencingInline.inlines = [SelfReferencingInline]

    @admin.register(User)
    class SampleModelAdmin(ModelAdmin):
        inlines = [SelfReferencingInline]
        nested_inlines_max_depth = 3

    errors = run_checks(
        app_configs=[apps.get_app_config("example")],
        tags=[Tags.admin],
    )

    assert errors == []


@pytest.mark.django_db
def test_nested_inlines_ambiguous_relation_is_reported_at_startup():
    admin.site.unregister(User)

    class AmbiguousInline(TabularInline):
        model = TagUserNote  # related to both sides of the User/Tag relation

    class UserTagInline(StackedInline):
        model = User.tags.through
        inlines = [AmbiguousInline]

    @admin.register(User)
    class SampleModelAdmin(ModelAdmin):
        inlines = [UserTagInline]

    errors = run_checks(
        app_configs=[apps.get_app_config("example")],
        tags=[Tags.admin],
    )

    assert len(errors) == 1
    assert errors[0].id == "unfold.E002"
    assert "through more than one relation" in errors[0].msg


@pytest.mark.django_db
def test_nested_inlines_named_relation_is_accepted():
    admin.site.unregister(User)

    class NamedInline(TabularInline):
        model = TagUserNote
        nested_parent_field = "tag"

    class UserTagInline(StackedInline):
        model = User.tags.through
        inlines = [NamedInline]

    @admin.register(User)
    class SampleModelAdmin(ModelAdmin):
        inlines = [UserTagInline]

    errors = run_checks(
        app_configs=[apps.get_app_config("example")],
        tags=[Tags.admin],
    )

    assert errors == []
