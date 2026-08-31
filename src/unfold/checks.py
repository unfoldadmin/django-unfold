from typing import Any

from django.contrib.admin.checks import ModelAdminChecks
from django.contrib.admin.options import BaseModelAdmin
from django.contrib.auth.models import Permission
from django.core import checks
from django.core.checks import CheckMessage
from django.core.exceptions import ImproperlyConfigured

from unfold.dataclasses import UnfoldAction


class UnfoldModelAdminChecks(ModelAdminChecks):
    def check(self, admin_obj: BaseModelAdmin, **kwargs) -> list[CheckMessage]:
        return [
            *super().check(admin_obj, **kwargs),
            *self._check_unfold_action_permission_methods(admin_obj),
            *self._check_nested_inlines(admin_obj),
        ]

    def _check_nested_inlines(self, obj: Any) -> list[checks.Error]:
        """
        Walk the tree of nested inlines and report what would otherwise only
        fail once somebody opens the changeform.

        A chain where an inline ends up being its own descendant never
        terminates, because every level also renders a template form used for
        adding new records, so it needs an explicit depth limit. And an inline
        nested below an intermediary model has to reach its own model through
        exactly one relation.
        """
        if not getattr(obj, "inlines", None):
            return []

        # Asked the same way `_build_form_nested_formsets()` asks, so that the
        # checks and the guards they stand in for can not disagree.
        get_max_depth = getattr(obj, "get_nested_inlines_max_depth", None)
        check_recursion = get_max_depth is not None and get_max_depth() is None

        errors = []
        reported = set()
        visited = set()

        def report(error_id: str, message: str, hint: str | None = None) -> None:
            if message in reported:
                return

            reported.add(message)
            errors.append(
                checks.Error(message, hint=hint, obj=obj.__class__, id=error_id)
            )

        def walk(inline_class: type, chain: tuple[type, ...]) -> None:
            if inline_class in chain:
                if check_recursion:
                    cycle = (*chain[chain.index(inline_class) :], inline_class)
                    names = " -> ".join(item.__name__ for item in cycle)
                    report(
                        "unfold.E001",
                        f"{obj.__class__.__name__} declares nested inlines which "
                        f"contain themselves ({names}).",
                        "Such a chain has no natural end. Set "
                        f"'nested_inlines_max_depth' on {obj.__class__.__name__} "
                        "to define how many levels of nested inlines are "
                        "rendered.",
                    )
                return

            for nested_class in getattr(inline_class, "inlines", ()):
                if (inline_class, nested_class) not in visited:
                    visited.add((inline_class, nested_class))

                    try:
                        obj._get_nested_parent_field(inline_class.model, nested_class)
                    except ImproperlyConfigured as error:
                        report("unfold.E002", str(error))
                        continue

                walk(nested_class, (*chain, inline_class))

        for inline_class in obj.inlines:
            walk(inline_class, ())

        return errors

    def _check_unfold_action_permission_methods(self, obj: Any) -> list[checks.Error]:
        """
        Actions with an allowed_permission attribute require the ModelAdmin to
        implement a has_<perm>_permission() method for each permission.
        """
        actions: list[UnfoldAction] = [
            *obj._get_base_actions_list(),
            *obj._get_base_actions_detail(),
            *obj._get_base_actions_row(),
            *obj._get_base_actions_submit_line(),
        ]
        errors = []
        for action in actions:
            if not hasattr(action.method, "allowed_permissions"):
                continue

            for permission in action.method.allowed_permissions:
                # Check the existence of Django permission
                if "." in permission:
                    app_label, codename = permission.split(".")

                    if not Permission.objects.filter(
                        content_type__app_label=app_label,
                        codename=codename,
                    ).exists():
                        errors.append(
                            checks.Error(
                                f"@action decorator on {action.method.original_function_name}() in class {obj.__class__.__name__} specifies permission {permission} which does not exists.",  # type: ignore
                                obj=obj.__class__,
                                id="admin.E129",
                            )
                        )

                    continue

                # Check the permission method existence
                method_name = f"has_{permission}_permission"
                if not hasattr(obj, method_name):
                    errors.append(
                        checks.Error(
                            f"{obj.__class__.__name__} must define a {method_name}() method for the {action.method.original_function_name}() action.",  # type: ignore
                            obj=obj.__class__,
                            id="admin.E129",
                        )
                    )

        return errors
