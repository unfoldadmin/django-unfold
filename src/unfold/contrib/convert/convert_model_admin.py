from django.contrib import admin

from unfold.admin import ModelAdmin, StackedInline, TabularInline


def convert_model_admin_to_unfold(admin_site: admin.AdminSite | None = None) -> None:
    """
    Automatically convert all registered admin classes to work with django-unfold.

    This function:
    1. Finds all admin classes that are not subclasses of unfold.admin.ModelAdmin
    2. Unregisters them
    3. Creates new classes that inherit from both the original admin and unfold.admin.ModelAdmin
    4. Fixes any inlines by creating new classes that inherit from unfold inline classes
    5. Registers the new classes

    Args:
        admin_site: The admin site to convert. Defaults to django.contrib.admin.site

    """

    admin_site = admin_site or admin.site

    # Get a copy of the registry to avoid modification during iteration
    registry_items = list(admin_site._registry.items())

    for model, model_admin in registry_items:
        # Skip if already using unfold.admin.ModelAdmin
        if isinstance(model_admin, ModelAdmin):
            continue

        # Get the original admin class
        original_admin_class = model_admin.__class__

        # Create a new admin class that inherits from both original and unfold ModelAdmin
        new_admin_attrs = {}

        # Handle inlines if they exist
        if getattr(model_admin, "inlines", None):
            fixed_inlines = [
                _make_inline(inline_class) for inline_class in model_admin.inlines
            ]
            new_admin_attrs["inlines"] = tuple(fixed_inlines)

        # Create the new admin class
        new_admin_name = f"Unfold{original_admin_class.__name__}"
        new_admin_class = type(
            new_admin_name,
            (ModelAdmin, original_admin_class),
            new_admin_attrs,
        )

        # Unregister the old admin and register the new one
        admin_site.unregister(model)
        admin_site.register(model, new_admin_class)


def _make_inline(inline_class: type) -> type:
    if issubclass(inline_class, (TabularInline, StackedInline)):
        return inline_class

    # Determine which unfold inline base to use
    unfold_base = None
    if hasattr(inline_class, "__bases__"):
        for base in inline_class.__bases__:
            if hasattr(base, "__name__"):
                if "TabularInline" in base.__name__:
                    unfold_base = TabularInline
                    break
                if "StackedInline" in base.__name__:
                    unfold_base = StackedInline
                    break

    # Default to TabularInline if we can't determine the type
    if unfold_base is None:
        unfold_base = TabularInline

    # Create new inline class
    new_inline_name = f"Unfold{inline_class.__name__}"
    return type(
        new_inline_name,
        (inline_class, unfold_base),
        {},
    )
