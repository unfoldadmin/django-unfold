from django.core.exceptions import PermissionDenied


def action(
    function=None, *, permissions=None, description=None, url_path=None, attrs=None
):
    def decorator(func):
        def inner(model_admin, request, *args, **kwargs):
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
    function=None,
    *,
    boolean=None,
    ordering=None,
    description=None,
    empty_value=None,
    label=None,
    header=None,
):
    def decorator(func):
        if boolean is not None and empty_value is not None:
            raise ValueError(
                "The boolean and empty_value arguments to the @display "
                "decorator are mutually exclusive."
            )
        if boolean is not None:
            func.boolean = boolean
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
