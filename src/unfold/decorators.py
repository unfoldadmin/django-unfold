from collections.abc import Callable, Iterable
from functools import wraps
from typing import TYPE_CHECKING, Any

from django.core.exceptions import PermissionDenied
from django.db.models import Model
from django.db.models.expressions import BaseExpression, Combinable
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

if TYPE_CHECKING:
    from django_stubs_ext import StrOrPromise


from unfold.admin import ModelAdmin
from unfold.dataclasses import ActionDialog
from unfold.enums import ActionVariant
from unfold.forms import BaseDialogForm


def action(
    function: Callable | None = None,
    *,
    permissions: Iterable[str] | None = None,
    description: "StrOrPromise | None" = None,
    url_path: str | None = None,
    attrs: dict[str, Any] | None = None,
    icon: str | None = None,
    variant: ActionVariant | None = ActionVariant.DEFAULT,
    dialog: ActionDialog | None = None,
    extra_options: dict[str, Any] | None = None,
) -> Callable:
    def decorator(func: Callable) -> Callable[..., HttpResponse | None]:
        function_name: str = func.__name__  # ty: ignore[missing-attribute]

        @wraps(func)
        def inner(
            model_admin: ModelAdmin,
            request: HttpRequest,
            *args: Any,
            **kwargs: Any,
        ) -> HttpResponse | None:
            if permissions:
                permission_rules = []

                for permission in permissions:
                    if "." in permission:
                        permission_rules.append(permission)
                    else:
                        # Permissions methods have following syntax: has_<some>_permission(self, request, obj=None):
                        # But obj is not examined by default in django admin and it would also require additional
                        # fetch from database, therefore it is not supported yet
                        permission_rules.append(
                            getattr(model_admin, f"has_{permission}_permission")
                        )

                has_detail_action = function_name in model_admin._extract_action_names(
                    model_admin.actions_detail
                )
                has_submit_line_action = (
                    function_name
                    in model_admin._extract_action_names(
                        model_admin.actions_submit_line
                    )
                )

                permission_checks = []

                for permission_rule in permission_rules:
                    if isinstance(permission_rule, str) and "." in permission_rule:
                        permission_checks.append(
                            request.user.has_perm(permission_rule)  # ty: ignore[missing-union-attribute]
                        )
                    elif has_detail_action or has_submit_line_action:
                        permission_checks.append(
                            permission_rule(request, kwargs.get("object_id"))  # ty: ignore[not-callable]
                        )
                    else:
                        permission_checks.append(permission_rule(request))  # ty: ignore[not-callable]

                if not all(permission_checks):
                    raise PermissionDenied

            if dialog:
                form_class = dialog.get("form_class") or BaseDialogForm
                form = form_class(
                    data=request.POST or None,
                    request=request,
                    object_id=kwargs.get("object_id"),
                )

                if form.is_valid():
                    return func(model_admin, request, form, *args, **kwargs)

                return render(
                    request,
                    "unfold/helpers/dialog.html",
                    {
                        "dialog": dialog,
                        "form": form,
                        "form_submit_text": dialog.get("form_submit_text", ""),
                    },
                )

            return func(model_admin, request, *args, **kwargs)

        if permissions is not None:
            inner.allowed_permissions = permissions  # ty: ignore[missing-attribute]

        if description is not None:
            inner.short_description = description  # ty: ignore[missing-attribute]

        if url_path is not None:
            inner.url_path = url_path  # ty: ignore[missing-attribute]

        if icon is not None:
            inner.icon = icon  # ty: ignore[missing-attribute]

        if dialog is not None:
            inner.dialog = dialog  # ty: ignore[missing-attribute]

        if variant is not None:
            inner.variant = variant  # ty: ignore[missing-attribute]
        else:
            inner.variant = ActionVariant.DEFAULT  # ty: ignore[missing-attribute]

        if extra_options is None:
            inner.extra_options = {}  # ty: ignore[missing-attribute]
        else:
            inner.extra_options = extra_options  # ty: ignore[missing-attribute]

        inner.attrs = attrs or {}  # ty: ignore[missing-attribute]
        inner.original_function_name = function_name  # ty: ignore[missing-attribute]
        return inner

    if function is None:
        return decorator

    return decorator(function)


def display(
    function: Callable[[Model], Any] | None = None,
    *,
    boolean: bool | None = None,
    image: bool | None = None,
    ordering: str | Combinable | BaseExpression | None = None,
    description: "StrOrPromise | None" = None,
    empty_value: str | None = None,
    dropdown: bool | None = None,
    label: "bool | StrOrPromise | dict[str, str] | None" = None,
    header: bool | None = None,
    wrapper_class: str | None = None,
    formatting: str | None = None,
) -> Callable:
    def decorator(func: Callable[[Model], Any]) -> Callable:
        if boolean is not None and empty_value is not None:
            raise ValueError(
                "The boolean and empty_value arguments to the @display "
                "decorator are mutually exclusive."
            )
        if boolean is not None:
            func.boolean = boolean  # ty: ignore[missing-attribute]
        if image is not None:
            func.image = image  # ty: ignore[missing-attribute]
        if ordering is not None:
            func.admin_order_field = ordering  # ty: ignore[missing-attribute]
        if description is not None:
            func.short_description = description  # ty: ignore[missing-attribute]
        if empty_value is not None:
            func.empty_value_display = empty_value  # ty: ignore[missing-attribute]
        if label is not None:
            func.label = label  # ty: ignore[missing-attribute]
        if header is not None:
            func.header = header  # ty: ignore[missing-attribute]
        if dropdown is not None:
            func.dropdown = dropdown  # ty: ignore[missing-attribute]
        if wrapper_class is not None:
            func.wrapper_class = wrapper_class  # ty: ignore[missing-attribute]
        if formatting is not None:
            func.formatting = formatting  # ty: ignore[missing-attribute]

        return func

    if function is None:
        return decorator
    else:
        return decorator(function)
