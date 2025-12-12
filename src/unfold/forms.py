from collections.abc import Generator
from typing import Any, Union

from django import forms
from django.contrib.admin.forms import (
    AdminAuthenticationForm,
)
from django.contrib.admin.forms import (
    AdminPasswordChangeForm as BaseAdminOwnPasswordChangeForm,
)
from django.contrib.admin.views.main import ChangeListSearchForm
from django.contrib.auth.forms import (
    AdminPasswordChangeForm as BaseAdminPasswordChangeForm,
)
from django.contrib.auth.models import User
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet
from django.core.paginator import Page, Paginator
from django.db.models import QuerySet
from django.forms import BaseInlineFormSet
from django.http import HttpRequest

from unfold.fields import UnfoldAdminField, UnfoldAdminReadonlyField

try:
    from django.contrib.auth.forms import AdminUserCreationForm as BaseUserCreationForm
except ImportError:
    from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.admin.helpers import AdminForm as BaseAdminForm
from django.contrib.admin.helpers import Fieldline as BaseFieldline
from django.contrib.admin.helpers import Fieldset as BaseFieldset
from django.contrib.auth.forms import ReadOnlyPasswordHashWidget
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from unfold.widgets import (
    BASE_INPUT_CLASSES,
    INPUT_CLASSES,
    UnfoldAdminPasswordInput,
    UnfoldAdminRadioSelectWidget,
    UnfoldAdminSelectWidget,
)


class UnfoldReadOnlyPasswordHashWidget(ReadOnlyPasswordHashWidget):
    pass


class ActionForm(forms.Form):
    action = forms.ChoiceField(
        label="",
        widget=UnfoldAdminSelectWidget(
            {
                "class": " ".join(
                    [
                        "group-[.changelist-actions]:appearance-none",
                        "group-[.changelist-actions]:!bg-white/20",
                        "group-[.changelist-actions]:font-medium",
                        "group-[.changelist-actions]:grow",
                        "group-[.changelist-actions]:px-2",
                        "group-[.changelist-actions]:py-1",
                        "group-[.changelist-actions]:pr-8",
                        "group-[.changelist-actions]:rounded-default",
                        "group-[.changelist-actions]:!text-current",
                        "group-[.changelist-actions]:truncate",
                        "group-[.changelist-actions]:!outline-primary-400",
                        "group-[.changelist-actions]:dark:!outline-primary-700",
                        "group-[.changelist-actions]:*:text-base-700",
                        "group-[.changelist-actions]:lg:w-72",
                    ]
                ),
                "aria-label": _("Select action to run"),
                "x-model": "action",
            }
        ),
    )

    select_across = forms.BooleanField(
        label="",
        required=False,
        initial=0,
        widget=forms.HiddenInput(
            {
                "class": "select-across",
                "x-model": "selectAcross",
            }
        ),
    )


class AuthenticationForm(AdminAuthenticationForm):
    def __init__(
        self,
        request: HttpRequest | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(request, *args, **kwargs)

        self.fields["username"].widget.attrs["autofocus"] = ""

        self.fields["username"].widget.attrs["class"] = " ".join(BASE_INPUT_CLASSES)
        self.fields["password"].widget.attrs["class"] = " ".join(BASE_INPUT_CLASSES)


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
        user: User,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(user, *args, **kwargs)

        self.fields["password1"].widget.attrs["class"] = " ".join(INPUT_CLASSES)
        self.fields["password2"].widget.attrs["class"] = " ".join(INPUT_CLASSES)


class AdminOwnPasswordChangeForm(BaseAdminOwnPasswordChangeForm):
    def __init__(self, user: User, *args, **kwargs) -> None:
        super().__init__(user, *args, **kwargs)

        self.fields["old_password"].widget.attrs["class"] = " ".join(INPUT_CLASSES)
        self.fields["new_password1"].widget.attrs["class"] = " ".join(INPUT_CLASSES)
        self.fields["new_password2"].widget.attrs["class"] = " ".join(INPUT_CLASSES)


class AdminForm(BaseAdminForm):
    def __iter__(self) -> Generator["Fieldset", None, None]:
        for name, options in self.fieldsets:
            yield Fieldset(
                self.form,
                name,
                readonly_fields=self.readonly_fields,
                model_admin=self.model_admin,
                **options,
            )


class Fieldset(BaseFieldset):
    def __iter__(self) -> Generator["Fieldline", None, None]:
        for field in self.fields:
            yield Fieldline(
                self.form, field, self.readonly_fields, model_admin=self.model_admin
            )


class Fieldline(BaseFieldline):
    def __iter__(
        self,
    ) -> Generator[Union["UnfoldAdminReadonlyField", "UnfoldAdminField"], None, None]:
        for i, field in enumerate(self.fields):
            if field in self.readonly_fields:
                yield UnfoldAdminReadonlyField(
                    self.form, field, is_first=(i == 0), model_admin=self.model_admin
                )
            else:
                yield UnfoldAdminField(self.form, field, is_first=(i == 0))


class PaginationFormSetMixin:
    queryset: QuerySet | None = None
    request: HttpRequest | None = None
    per_page: int | None = None

    def __init__(
        self,
        request: HttpRequest | None = None,
        per_page: int | None = None,
        *args,
        **kwargs,
    ):
        self.request = request
        self.per_page = per_page

        super().__init__(*args, **kwargs)

        if self.per_page:
            self.paginator = Paginator(self.queryset, self.per_page)
            self.page = self.get_page(self.paginator, self.get_page_num())
            self._queryset = self.page.object_list

    def get_pagination_key(self) -> str:
        return f"{self.prefix}-page"

    def get_page_num(self) -> int:
        page = self.request.GET.get(self.get_pagination_key())
        if page and page.isnumeric() and page > "0":
            return int(page)

        page = self.request.POST.get(self.get_pagination_key())
        if page and page.isnumeric() and page > "0":
            return int(page)

        return 1

    def get_page(self, paginator: Paginator, page: int) -> Page:
        if page <= paginator.num_pages:
            return paginator.page(page)

        return paginator.page(1)


class PaginationInlineFormSet(PaginationFormSetMixin, BaseInlineFormSet):
    pass


class PaginationGenericInlineFormSet(PaginationFormSetMixin, BaseGenericInlineFormSet):
    pass


class DatasetChangeListSearchForm(ChangeListSearchForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        search_var = kwargs.pop("search_var")
        super().__init__(*args, **kwargs)

        self.fields = {
            search_var: forms.CharField(required=False, strip=False),
        }
