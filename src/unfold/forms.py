from django import forms
from django.contrib.admin.forms import (
    AdminAuthenticationForm,
)
from django.contrib.admin.forms import (
    AdminPasswordChangeForm as BaseAdminOwnPasswordChangeForm,
)
from django.contrib.auth.forms import (
    AdminPasswordChangeForm as BaseAdminPasswordChangeForm,
)
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.utils.translation import gettext_lazy as _

from .widgets import BASE_INPUT_CLASSES, INPUT_CLASSES, SELECT_CLASSES


class ActionForm(forms.Form):
    action = forms.ChoiceField(
        label="",
        widget=forms.Select({"class": " ".join([*SELECT_CLASSES, "w-72"])}),
    )

    select_across = forms.BooleanField(
        label="",
        required=False,
        initial=0,
        widget=forms.HiddenInput({"class": "select-across"}),
    )


class AuthenticationForm(AdminAuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        self.fields["username"].widget.attrs["class"] = " ".join(BASE_INPUT_CLASSES)
        self.fields["password"].widget.attrs["class"] = " ".join(BASE_INPUT_CLASSES)


class UserCreationForm(BaseUserCreationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        self.fields["password1"].widget.attrs["class"] = " ".join(INPUT_CLASSES)
        self.fields["password2"].widget.attrs["class"] = " ".join(INPUT_CLASSES)


class UserChangeForm(BaseUserChangeForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        self.fields["password"].help_text = _(
            "Raw passwords are not stored, so there is no way to see this "
            "user’s password, but you can change the password using "
            '<a href="{}" class="text-primary-600 underline whitespace-nowrap">this form</a>.'
        )

        password = self.fields.get("password")
        if password:
            password.help_text = password.help_text.format("../password/")


class AdminPasswordChangeForm(BaseAdminPasswordChangeForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        self.fields["password1"].widget.attrs["class"] = " ".join(INPUT_CLASSES)
        self.fields["password2"].widget.attrs["class"] = " ".join(INPUT_CLASSES)


class AdminOwnPasswordChangeForm(BaseAdminOwnPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(kwargs.pop("user"), *args, **kwargs)

        self.fields["old_password"].widget.attrs["class"] = " ".join(INPUT_CLASSES)
        self.fields["new_password1"].widget.attrs["class"] = " ".join(INPUT_CLASSES)
        self.fields["new_password2"].widget.attrs["class"] = " ".join(INPUT_CLASSES)
