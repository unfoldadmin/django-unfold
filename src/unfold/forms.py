from typing import Optional

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

try:
    from django.contrib.auth.forms import AdminUserCreationForm as BaseUserCreationForm
except ImportError:
    from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.forms import ReadOnlyPasswordHashWidget
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.http import HttpRequest
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .widgets import (
    BASE_INPUT_CLASSES,
    INPUT_CLASSES,
    SELECT_CLASSES,
    UnfoldAdminPasswordInput,
    UnfoldAdminRadioSelectWidget,
)


class UnfoldReadOnlyPasswordHashWidget(ReadOnlyPasswordHashWidget):
    pass


class ActionForm(forms.Form):
    action = forms.ChoiceField(
        label="",
        widget=forms.Select(
            {
                "class": " ".join([*SELECT_CLASSES, "max-w-full", "lg:!w-64"]),
                "aria-label": _("Select action to run"),
                "x-model": "action",
            }
        ),
    )

    select_across = forms.BooleanField(
        label="",
        required=False,
        initial=0,
        widget=forms.HiddenInput({"class": "select-across"}),
    )


class AuthenticationForm(AdminAuthenticationForm):
    def __init__(
        self,
        request: Optional[HttpRequest] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(request, *args, **kwargs)

        self.fields["username"].widget.attrs["class"] = " ".join(BASE_INPUT_CLASSES)
        self.fields["password"].widget.attrs["class"] = " ".join(BASE_INPUT_CLASSES)


class UserCreationForm(BaseUserCreationForm):
    def __init__(
        self,
        request: Optional[HttpRequest] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(request, *args, **kwargs)

        self.fields["password1"].widget = UnfoldAdminPasswordInput(
            attrs={"autocomplete": "new-password"}
        )
        self.fields["password2"].widget = UnfoldAdminPasswordInput(
            attrs={"autocomplete": "new-password"}
        )

        if "usable_password" in self.fields:
            self.fields["usable_password"].widget = UnfoldAdminRadioSelectWidget(
                choices=self.fields["usable_password"].choices,
            )


class UserChangeForm(BaseUserChangeForm):
    def __init__(
        self,
        request: Optional[HttpRequest] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(request, *args, **kwargs)
        self.fields["password"].widget = UnfoldReadOnlyPasswordHashWidget()

        self.fields["password"].help_text = _(
            "Raw passwords are not stored, so there is no way to see this "
            "user’s password, but you can change the password using "
            '<a href="{}" class="text-primary-600 dark:text-primary-500">this form</a>.'
        )

        password = self.fields.get("password")
        if password:
            password.help_text = mark_safe(password.help_text.format("../password/"))


class AdminPasswordChangeForm(BaseAdminPasswordChangeForm):
    def __init__(
        self,
        request: Optional[HttpRequest] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(request, *args, **kwargs)

        self.fields["password1"].widget.attrs["class"] = " ".join(INPUT_CLASSES)
        self.fields["password2"].widget.attrs["class"] = " ".join(INPUT_CLASSES)


class AdminOwnPasswordChangeForm(BaseAdminOwnPasswordChangeForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(kwargs.pop("user"), *args, **kwargs)

        self.fields["old_password"].widget.attrs["class"] = " ".join(INPUT_CLASSES)
        self.fields["new_password1"].widget.attrs["class"] = " ".join(INPUT_CLASSES)
        self.fields["new_password2"].widget.attrs["class"] = " ".join(INPUT_CLASSES)
