def action(
    function=None, *, permissions=None, description=None, url_path=None, attrs=None
):
    def decorator(func):
        if permissions is not None:
            func.allowed_permissions = permissions
        if description is not None:
            func.short_description = description
        if url_path is not None:
            func.url_path = url_path
        func.attrs = attrs or {}
        return func

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
