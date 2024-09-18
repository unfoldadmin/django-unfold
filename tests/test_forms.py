from django.test import RequestFactory
from example.models import User

from unfold.forms import (
    AdminPasswordChangeForm,
    AuthenticationForm,
    UserChangeForm,
    UserCreationForm,
)

"""
These tests are here mainly to test, that given forms are able to init using default args/kwargs
"""


def test_authenticate_form_init(rf: RequestFactory):
    form = AuthenticationForm(
        request=rf.get("/"), data={"username": "test", "password": "test"}
    )
    assert "username" in form.fields
    assert "password" in form.fields


def test_user_creation_form():
    form = UserCreationForm(
        data={"username": "test", "password1": "test", "password2": "test"}
    )
    assert "username" in form.fields
    assert "password1" in form.fields
    assert "password2" in form.fields


def test_user_change_form():
    form = UserChangeForm(data={"username": "test", "password": "test"})
    password_field = form.fields["password"]
    expected_password_help_text = (
        "Raw passwords are not stored, so there is no way to see this user’s password, but you can change the password "
        'using <a href="../password/" class="text-primary-600 dark:text-primary-500">this form</a>.'
    )
    assert password_field.help_text == expected_password_help_text
    assert hasattr(password_field.help_text, "__html__")  # its safe string
    assert password_field.widget == form.fields["password"].widget


def test_admin_password_change_form():
    form = AdminPasswordChangeForm(
        user=User(),
        data={"old_password": "old", "password1": "test", "password2": "test"},
    )
    assert bool(form)
