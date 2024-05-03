from typing import Any, List

from django.contrib.admin.checks import ModelAdminChecks
from django.contrib.admin.options import BaseModelAdmin
from django.core import checks

from .dataclasses import UnfoldAction


class UnfoldModelAdminChecks(ModelAdminChecks):
    def check(self, admin_obj: BaseModelAdmin, **kwargs) -> List[checks.Error]:
        return [
            *super().check(admin_obj, **kwargs),
            *self._check_unfold_action_permission_methods(admin_obj),
        ]

    def _check_unfold_action_permission_methods(self, obj: Any) -> List[checks.Error]:
        """
        Actions with an allowed_permission attribute require the ModelAdmin to
        implement a has_<perm>_permission() method for each permission.
        """
        actions: List[UnfoldAction] = [
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
                method_name = f"has_{permission}_permission"
                if not hasattr(obj, method_name):
                    errors.append(
                        checks.Error(
                            f"{obj.__class__.__name__} must define a {method_name}() method for the {action.method.__name__} action.",
                            obj=obj.__class__,
                            id="admin.E129",
                        )
                    )
        return errors
