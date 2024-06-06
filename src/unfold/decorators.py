from typing import Any, Callable, Dict, Iterable, Optional, Union

from django.contrib.admin.options import BaseModelAdmin
from django.core.exceptions import PermissionDenied
from django.db.models import Model
from django.db.models.expressions import BaseExpression, Combinable
from django.http import HttpRequest, HttpResponse

from .typing import ActionFunction


def action(
    function: Optional[Callable] = None,
    *,
    permissions: Optional[Iterable[str]] = None,
    description: Optional[str] = None,
    url_path: Optional[str] = None,
    attrs: Optional[Dict[str, Any]] = None,
) -> ActionFunction:
    def decorator(func: Callable) -> ActionFunction:
        def inner(
            model_admin: BaseModelAdmin,
            request: HttpRequest,
            *args: Any,
            **kwargs,
        ) -> Optional[HttpResponse]:
            if permissions:
                permission_checks = (
                    getattr(model_admin, f"has_{permission}_permission")
                    for permission in permissions
                )
                # TODO add obj parameter into has_permission method call.
                # Permissions methods have following syntax: has_<some>_permission(self, request, obj=None):
                # But obj is not examined by default in django admin and it would also require additional
                # fetch from database, therefore it is not supported yet
                if not any(
                    has_permission(request) for has_permission in permission_checks
                ):
                    raise PermissionDenied
            return func(model_admin, request, *args, **kwargs)

        if permissions is not None:
            inner.allowed_permissions = permissions
        if description is not None:
            inner.short_description = description
        if url_path is not None:
            inner.url_path = url_path
        inner.attrs = attrs or {}
        return inner

    if function is None:
        return decorator
    else:
        return decorator(function)


def display(
    function: Optional[Callable[[Model], Any]] = None,
    *,
    boolean: Optional[bool] = None,
    image: Optional[bool] = None,
    ordering: Optional[Union[str, Combinable, BaseExpression]] = None,
    description: Optional[str] = None,
    empty_value: Optional[str] = None,
    label: Optional[Union[bool, str, Dict[str, str]]] = None,
    header: Optional[bool] = None,
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

        return func

    if function is None:
        return decorator
    else:
        return decorator(function)
