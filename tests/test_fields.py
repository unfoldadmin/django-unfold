import django
import pytest
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashWidget
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from example.admin import UserAdmin
from example.models import User

from unfold.fields import (
    UnfoldAdminAutocompleteModelChoiceField,
    UnfoldAdminField,
    UnfoldAdminMultipleAutocompleteModelChoiceField,
    UnfoldAdminReadonlyField,
)
from unfold.models.fields import JSONSchemaField
from unfold.sites import UnfoldAdminSite

NOT_CALLABLE = "NOT_CALLABLE"


class ExampleForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "file",
            "data",
            "content_type",
            "password",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password"].widget = ReadOnlyPasswordHashWidget()


@pytest.mark.django_db
def test_unfold_admin_readonly_field(user_factory):
    user = user_factory(username="sample@example.com")
    readonly_field = UnfoldAdminReadonlyField(
        form=ExampleForm(instance=user),
        field="username",
        is_first=True,
        model_admin=UserAdmin(get_user_model(), UnfoldAdminSite()),
    )

    assert "Username" in str(readonly_field.label_tag())
    assert "sample@example.com" == readonly_field.contents()
    assert not readonly_field.url


@pytest.mark.django_db
def test_unfold_admin_readonly_preprocess_field_string(user_factory):
    user = user_factory(username="sample@example.com")
    readonly_field = UnfoldAdminReadonlyField(
        form=ExampleForm(instance=user),
        field="custom_readonly_field",
        is_first=True,
        model_admin=UserAdmin(get_user_model(), UnfoldAdminSite()),
    )

    assert "Custom readonly field" in str(readonly_field.label_tag())
    assert readonly_field.contents() == "Custom readonly field"


@pytest.mark.django_db
def test_unfold_admin_readonly_preprocess_field_callable(user_factory):
    user = user_factory(username="sample@example.com")
    readonly_field = UnfoldAdminReadonlyField(
        form=ExampleForm(instance=user),
        field="another_readonly_field",
        is_first=True,
        model_admin=UserAdmin(get_user_model(), UnfoldAdminSite()),
    )

    assert "Another readonly field" in str(readonly_field.label_tag())
    assert readonly_field.contents() == "Another readonly field"


@pytest.mark.django_db
def test_unfold_admin_readonly_resolved_field(monkeypatch, user_factory):
    from unfold import fields

    def raise_attribute_error(*args, **kwargs):
        raise AttributeError("Mocked AttributeError for lookup_field")

    monkeypatch.setattr(fields, "lookup_field", raise_attribute_error)

    user = user_factory(username="sample@example.com")
    readonly_field = UnfoldAdminReadonlyField(
        form=ExampleForm(instance=user),
        field="content_type",
        is_first=True,
        model_admin=UserAdmin(get_user_model(), UnfoldAdminSite()),
    )

    assert not readonly_field.is_json
    assert not readonly_field.is_image
    assert not readonly_field.is_file
    assert "-" == readonly_field.contents()


@pytest.mark.django_db
def test_unfold_admin_readonly_field_boolean(user_factory):
    user = user_factory(username="sample2@example.com")
    readonly_field = UnfoldAdminReadonlyField(
        form=ExampleForm(instance=user),
        field="boolean_readonly_field",
        is_first=True,
        model_admin=UserAdmin(get_user_model(), UnfoldAdminSite()),
    )
    assert "check_small" in readonly_field.contents()


@pytest.mark.django_db
def test_unfold_admin_readonly_field_html(user_factory):
    user = user_factory(username="sample2@example.com")
    readonly_field = UnfoldAdminReadonlyField(
        form=ExampleForm(instance=user),
        field="html_readonly_field",
        is_first=True,
        model_admin=UserAdmin(get_user_model(), UnfoldAdminSite()),
    )
    assert "<b>HTML readonly field example-value</b>" in readonly_field.contents()


@pytest.mark.django_db
@pytest.mark.skipif(
    django.VERSION[:2] != (5, 2),
    reason="Only runs on Django 5.2",
)
def test_unfold_admin_readonly_field_password_older(user_factory):
    user = user_factory(username="sample2@example.com")
    readonly_field = UnfoldAdminReadonlyField(
        form=ExampleForm(instance=user),
        field="password",
        is_first=True,
        model_admin=UserAdmin(get_user_model(), UnfoldAdminSite()),
    )
    assert "No password set." in readonly_field.contents()


@pytest.mark.django_db
@pytest.mark.skipif(
    django.VERSION[:2] <= (5, 2),
    reason="Requires Django > 5.2",
)
def test_unfold_admin_readonly_field_password(user_factory):
    user = user_factory(username="sample2@example.com")
    readonly_field = UnfoldAdminReadonlyField(
        form=ExampleForm(instance=user),
        field="password",
        is_first=True,
        model_admin=UserAdmin(get_user_model(), UnfoldAdminSite()),
    )
    assert "-" in readonly_field.contents()


@pytest.mark.django_db
def test_unfold_admin_readonly_field_url(user_factory):
    user2 = user_factory(username="sample2@example.com", url="https://example.com")
    readonly_field = UnfoldAdminReadonlyField(
        form=ExampleForm(instance=user2),
        field="url",
        is_first=True,
        model_admin=UserAdmin(get_user_model(), UnfoldAdminSite()),
    )
    assert (
        '<a href="https://example.com" class="text-link">https://example.com</a>'
        == readonly_field.contents()
    )


@pytest.mark.django_db
def test_unfold_admin_readonly_field_file(user_factory):
    user2 = user_factory(username="sample2@example.com", file="test.txt")
    readonly_field = UnfoldAdminReadonlyField(
        form=ExampleForm(instance=user2),
        field="file",
        is_first=True,
        model_admin=UserAdmin(get_user_model(), UnfoldAdminSite()),
    )
    assert '<a href="/test.txt">test.txt</a>' == readonly_field.contents()
    assert "/test.txt" in readonly_field.url


@pytest.mark.django_db
def test_unfold_admin_readonly_field_image(user_factory):
    user2 = user_factory(username="sample2@example.com", image="test.jpg")
    readonly_field = UnfoldAdminReadonlyField(
        form=ExampleForm(instance=user2),
        field="image",
        is_first=True,
        model_admin=UserAdmin(get_user_model(), UnfoldAdminSite()),
    )

    assert "/test.jpg" in readonly_field.url
    assert '<a href="/test.jpg">test.jpg</a>' == readonly_field.contents()
    assert readonly_field.is_image
    assert readonly_field.is_file


@pytest.mark.django_db
def test_unfold_admin_readonly_field_url_no_file(user_factory):
    user = user_factory(username="sample@example.com")
    readonly_field = UnfoldAdminReadonlyField(
        form=ExampleForm(instance=user),
        field="file",
        is_first=True,
        model_admin=UserAdmin(get_user_model(), UnfoldAdminSite()),
    )

    assert readonly_field.is_file
    assert "" == readonly_field.contents()
    assert not readonly_field.url


@pytest.mark.django_db
def test_unfold_admin_readonly_field_json(user_factory):
    user = user_factory(username="sample@example.com")
    readonly_field = UnfoldAdminReadonlyField(
        form=ExampleForm(instance=user),
        field="data",
        is_first=True,
        model_admin=UserAdmin(get_user_model(), UnfoldAdminSite()),
    )

    assert "highlight" in readonly_field.contents()
    assert readonly_field.is_json


@pytest.mark.django_db
def test_unfold_admin_readonly_field_json_pygments_not_installed(
    monkeypatch, user_factory
):
    from unfold import fields

    def pgyments_not_installed(*args, **kwargs):
        return None

    monkeypatch.setattr(fields, "prettify_json", pgyments_not_installed)

    user = user_factory(username="sample@example.com")
    readonly_field = UnfoldAdminReadonlyField(
        form=ExampleForm(instance=user),
        field="data",
        is_first=True,
        model_admin=UserAdmin(get_user_model(), UnfoldAdminSite()),
    )

    assert "-" in readonly_field.contents()


@pytest.mark.django_db
def test_unfold_admin_readonly_field_fk_no_adminpage(user_factory):
    user = user_factory(
        username="sample@example.com",
        content_type=ContentType.objects.get(app_label="example", model="user"),
    )

    readonly_field = UnfoldAdminReadonlyField(
        form=ExampleForm(instance=user),
        field="content_type",
        is_first=True,
        model_admin=UserAdmin(get_user_model(), UnfoldAdminSite()),
    )

    assert "Example | user" in readonly_field.contents()


@pytest.mark.django_db
def test_unfold_admin_readonly_field_fk_with_adminpage(user_factory, profile_factory):
    user = user_factory(
        username="sample@example.com",
        profile=profile_factory(name="Test Profile"),
    )

    readonly_field = UnfoldAdminReadonlyField(
        form=ExampleForm(instance=user),
        field="profile",
        is_first=True,
        model_admin=UserAdmin(get_user_model(), UnfoldAdminSite()),
    )

    assert (
        '<a href="/admin/example/profile/1/change/" class="text-link">Test Profile</a>'
        in readonly_field.contents()
    )


@pytest.mark.django_db
def test_unfold_admin_readonly_field_many_to_many(user_factory, tag_factory):
    user = user_factory(
        username="sample@example.com",
    )
    user.tags.add(tag_factory(name="Test Tag1"))
    user.tags.add(tag_factory(name="Test Tag2"))

    readonly_field = UnfoldAdminReadonlyField(
        form=ExampleForm(instance=user),
        field="tags",
        is_first=True,
        model_admin=UserAdmin(get_user_model(), UnfoldAdminSite()),
    )
    assert "Test Tag1, Test Tag2" in readonly_field.contents()


def test_unfold_admin_field():
    admin_field = UnfoldAdminField(form=ExampleForm(), field="username", is_first=True)
    assert (
        admin_field.label_tag()
        == '<label class="block font-semibold mb-2 text-font-important-light text-sm dark:text-font-important-dark required" for="id_username">Username<span class="text-red-600 dark:text-red-500">*</span></label>'
    )


@pytest.mark.django_db
def test_unfold_admin_autocomplete_field(user_factory):
    user = user_factory(username="sample@example.com")
    form = ExampleForm(instance=user)
    form.fields["username"] = UnfoldAdminAutocompleteModelChoiceField(
        label="Username",
        queryset=get_user_model().objects.all(),
        url_path="admin:index",
    )

    assert form.fields["username"].widget.attrs["data-ajax--url"] == "/admin/"


@pytest.mark.django_db
def test_unfold_admin_multiple_autocomplete_field(user_factory):
    user = user_factory(username="sample@example.com")
    form = ExampleForm(instance=user)
    form.fields["username"] = UnfoldAdminMultipleAutocompleteModelChoiceField(
        label="Username",
        queryset=get_user_model().objects.all(),
        url_path="admin:index",
    )

    assert form.fields["username"].widget.attrs["data-ajax--url"] == "/admin/"


@pytest.mark.django_db
def test_unfold_json_schema_field():
    user = User.objects.create(
        username="jsonschematest",
        password="password",
        data={
            "name": "John",
            "age": 25,
        },
    )
    user.full_clean()

    user.data = None
    user.full_clean()

    user.data = {
        "name": "Jane",
        "age": 25,
        "extra": "not allowed",
    }

    with pytest.raises(ValidationError):
        user.full_clean()

    user.data = {
        "name": "Jane",
        "age": "not_a_number",
    }

    with pytest.raises(ValidationError) as e:
        user.full_clean()

    assert "age" in str(e.value)


def test_unfold_json_schema_field_import_from_dotted_path():
    with pytest.raises(ImportError) as e:
        JSONSchemaField(schema="example.schemas.UserSchema")

    assert (
        "Could not import callable schema from dotted path 'example.schemas.UserSchema': No module named 'example.schemas'"
        in str(e.value)
    )


def test_unfold_json_schema_field_import_from_dotted_path_is_not_callable():
    with pytest.raises(ImportError) as e:
        JSONSchemaField(schema="tests.test_fields.NOT_CALLABLE")

    assert (
        "The imported schema object from 'tests.test_fields.NOT_CALLABLE' must be callable."
        in str(e.value)
    )
