from typing import Iterable, Optional, Tuple

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
from django.contrib.auth.models import AbstractUser
from django.utils.html import format_html

try:
    from django.contrib.auth.forms import AdminUserCreationForm as BaseUserCreationForm
except ImportError:
    from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.forms import ReadOnlyPasswordHashWidget
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.http import HttpRequest
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

        _apply_widget_classes_to_fields(
            self, ("username", "password"), BASE_INPUT_CLASSES
        )


class UserCreationForm(BaseUserCreationForm):
    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

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
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.fields["password"].widget = UnfoldReadOnlyPasswordHashWidget()

        self.fields["password"].help_text = format_html(
            _(
                "Raw passwords are not stored, so there is no way to see this "
                "user’s password, but you can change the password using "
                '<a href="{}" class="text-primary-600 dark:text-primary-500">this form</a>.'
            ),
            "../password/",
        )


class AdminPasswordChangeForm(BaseAdminPasswordChangeForm):
    def __init__(
        self,
        user: AbstractUser,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(user, *args, **kwargs)

        _apply_widget_classes_to_fields(self, ("password1", "password2"), INPUT_CLASSES)


class AdminOwnPasswordChangeForm(BaseAdminOwnPasswordChangeForm):
    def __init__(self, user: AbstractUser, *args, **kwargs) -> None:
        super().__init__(user, *args, **kwargs)

        _apply_widget_classes_to_fields(
            self, ("old_password", "new_password1", "new_password2"), INPUT_CLASSES
        )


def _apply_widget_classes_to_fields(
    form: forms.Form, fields: Tuple[str, ...], classes: Iterable[str]
) -> None:
    """
    Applies the predefined input classes to the specified fields of a form.

    Args:
        form (forms.BaseForm): The form instance to which the classes should be applied.
        fields (tuple[str, ...]): A tuple of field names whose widgets will have the classes applied.
    """
    input_classes: str = " ".join(classes)

    for field in fields:
        form.fields[field].widget.attrs["class"] = input_classes
