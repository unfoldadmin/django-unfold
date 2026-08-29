from typing import Any

from django.contrib.admin.checks import InlineModelAdminChecks, ModelAdminChecks
from django.contrib.admin.options import BaseModelAdmin
from django.contrib.auth.models import Permission
from django.core import checks
from django.core.checks import CheckMessage

from unfold.dataclasses import UnfoldAction


class UnfoldModelAdminChecks(ModelAdminChecks):
    def check(self, admin_obj: BaseModelAdmin, **kwargs) -> list[CheckMessage]:
        return [
            *super().check(admin_obj, **kwargs),
            *self._check_unfold_action_permission_methods(admin_obj),
            *self._check_autocomplete_dependencies(admin_obj),
            *self._check_duplicate_dependent_autocomplete_urls(admin_obj),
        ]

    def _check_autocomplete_dependencies(self, obj: Any) -> list[checks.Error]:
        if hasattr(obj, "_check_autocomplete_dependencies"):
            return obj._check_autocomplete_dependencies()
        return []

    def _check_duplicate_dependent_autocomplete_urls(
        self, obj: Any
    ) -> list[checks.Error]:
        names: list[str] = []
        inlines = getattr(obj, "inlines", ())
        if not isinstance(inlines, list | tuple):
            return []
        for inline_class in inlines:
            inline = inline_class(obj.model, obj.admin_site)
            if getattr(inline, "autocomplete_dependencies", None):
                names.append(inline.get_dependent_autocomplete_url_name())

        seen: set[str] = set()
        errors = []
        for name in names:
            if name in seen:
                errors.append(
                    checks.Error(
                        "Multiple inlines generate the same dependent autocomplete URL "
                        f"name '{name}'. Rename an inline class so each config owner "
                        "has a unique URL.",
                        obj=obj,
                        id="unfold.E009",
                    )
                )
            seen.add(name)
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


class UnfoldInlineModelAdminChecks(InlineModelAdminChecks):
    def check(self, inline_obj: BaseModelAdmin, **kwargs) -> list[CheckMessage]:
        return [
            *super().check(inline_obj, **kwargs),
            *self._check_autocomplete_dependencies(inline_obj),
        ]

    def _check_autocomplete_dependencies(self, obj: Any) -> list[checks.Error]:
        if hasattr(obj, "_check_autocomplete_dependencies"):
            return obj._check_autocomplete_dependencies()
        return []
