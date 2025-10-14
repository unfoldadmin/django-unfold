from collections.abc import Callable, Iterable
from typing import Any

from django.contrib.admin.options import BaseModelAdmin
from django.core.exceptions import PermissionDenied
from django.db.models import Model
from django.db.models.expressions import BaseExpression, Combinable
from django.http import HttpRequest, HttpResponse

from unfold.enums import ActionVariant
from unfold.typing import ActionFunction


def action(
    function: Callable | None = None,
    *,
    permissions: Iterable[str] | None = None,
    description: str | None = None,
    url_path: str | None = None,
    attrs: dict[str, Any] | None = None,
    icon: str | None = None,
    variant: ActionVariant | None = ActionVariant.DEFAULT,
) -> ActionFunction:
    def decorator(func: Callable) -> ActionFunction:
        def inner(
            model_admin: BaseModelAdmin,
            request: HttpRequest,
            *args: Any,
            **kwargs,
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

                has_detail_action = func.__name__ in model_admin._extract_action_names(
                    model_admin.actions_detail
                )
                has_submit_line_action = (
                    func.__name__
                    in model_admin._extract_action_names(
                        model_admin.actions_submit_line
                    )
                )

                permission_checks = []

                for permission_rule in permission_rules:
                    if isinstance(permission_rule, str) and "." in permission_rule:
                        permission_checks.append(request.user.has_perm(permission_rule))
                    elif has_detail_action or has_submit_line_action:
                        permission_checks.append(
                            permission_rule(request, kwargs.get("object_id"))
                        )
                    else:
                        permission_checks.append(permission_rule(request))

                if not all(permission_checks):
                    raise PermissionDenied
            return func(model_admin, request, *args, **kwargs)

        if permissions is not None:
            inner.allowed_permissions = permissions

        if description is not None:
            inner.short_description = description

        if url_path is not None:
            inner.url_path = url_path

        if icon is not None:
            inner.icon = icon

        if variant is not None:
            inner.variant = variant
        else:
            inner.variant = ActionVariant.DEFAULT

        inner.attrs = attrs or {}
        inner.original_function_name = func.__name__
        return inner

    if function is None:
        return decorator
    else:
        return decorator(function)


def display(
    function: Callable[[Model], Any] | None = None,
    *,
    boolean: bool | None = None,
    image: bool | None = None,
    ordering: str | Combinable | BaseExpression | None = None,
    description: str | None = None,
    empty_value: str | None = None,
    dropdown: bool | None = None,
    label: bool | str | dict[str, str] | None = None,
    header: bool | None = None,
) -> Callable:
    def decorator(func: Callable[[Model], Any]) -> Callable:
        if boolean is not None and empty_value is not None:
            raise ValueError(
                "The boolean and empty_value arguments to the @display "
                "decorator are mutually exclusive."
            )
        if boolean is not None:
            func.boolean = boolean
        if image is not None:
            func.image = image
        if ordering is not None:
            func.admin_order_field = ordering
        if description is not None:
            func.short_description = description
        if empty_value is not None:
            func.empty_value_display = empty_value
        if label is not None:
            func.label = label
        if header is not None:
            func.header = header
        if dropdown is not None:
            func.dropdown = dropdown

        return func

    if function is None:
        return decorator
    else:
        return decorator(function)
