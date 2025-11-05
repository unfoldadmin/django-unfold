from collections.abc import Callable
from typing import Any

from django.db.models import Model
from django.forms import Form
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.urls import reverse

from unfold.dataclasses import UnfoldAction
from unfold.enums import ActionVariant
from unfold.exceptions import UnfoldException


class ActionModelAdminMixin:
    """
    Adds support for various ModelAdmin actions (list, detail, row, submit line)
    """

    actions_list = ()  # Displayed in changelist at the top
    actions_list_hide_default = False
    actions_row = ()  # Displayed in changelist for each row in the table
    actions_detail = ()  # Displayed in changeform at the top
    actions_detail_hide_default = False
    actions_submit_line = ()  # Displayed in changeform in the submit line (form buttons)

    def changelist_view(
        self, request: HttpRequest, extra_context: dict[str, str] | None = None
    ) -> TemplateResponse:
        """
        Changelist contains `actions_list` and `actions_row` custom actions. In case of `actions_row` they
        are displayed in the each row of the table.
        """
        extra_context = extra_context or {}

        actions_row = [
            {
                "title": action.description,
                "icon": action.icon,
                "attrs": action.method.attrs,
                # This is just a path name as string and in template is used in {% url %} tag
                # with custom instance pk value
                "raw_path": f"{self.admin_site.name}:{action.action_name}",
            }
            for action in self.get_actions_row(request)
        ]

        # `actions_list` may contain custom structure with dropdowns so it is needed
        # to use `_get_actions_navigation` to build the final structure for the template
        actions_list = self._get_actions_navigation(
            self.actions_list, self.get_actions_list(request)
        )

        extra_context.update(
            {
                "actions_list_hide_default": self.actions_list_hide_default,
                "actions_list": actions_list,
                "actions_row": actions_row,
            }
        )

        return super().changelist_view(request, extra_context)

    def changeform_view(
        self,
        request: HttpRequest,
        object_id: str | None = None,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> Any:
        """
        Changeform contains `actions_submit_line` and `actions_detail` custom actions.
        """
        extra_context = extra_context or {}

        if object_id:
            # `actions_submit_line` is a list of actions that are displayed in the submit line they
            # are displayed as form buttons
            actions_submit_line = self.get_actions_submit_line(request, object_id)

            # `actions_detail` may contain custom structure with dropdowns so it is needed
            # to use `_get_actions_navigation` to build the final structure for the template
            actions_detail = self._get_actions_navigation(
                self.actions_detail,
                self.get_actions_detail(request, object_id),
                object_id,
            )

            extra_context.update(
                {
                    "actions_detail_hide_default": self.actions_detail_hide_default,
                    "actions_submit_line": actions_submit_line,
                    "actions_detail": actions_detail,
                }
            )

        return super().changeform_view(request, object_id, form_url, extra_context)

    def save_model(
        self, request: HttpRequest, obj: Model, form: Form, change: Any
    ) -> None:
        """
        When saving object, run all appropriate actions from `actions_submit_line`
        """
        super().save_model(request, obj, form, change)

        # After saving object, check if any button from `actions_submit_line` was pressed
        # and call the corresponding method
        for action in self.get_actions_submit_line(request, obj.pk):
            if action.action_name not in request.POST:
                continue

            action.method(request, obj)

    def get_unfold_action(self, action: str) -> UnfoldAction:
        """
        Converts action name into UnfoldAction object.
        """
        method = self._get_instance_method(action)

        return UnfoldAction(
            action_name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_{action}",
            method=method,
            description=self._get_action_description(method, action),
            path=getattr(method, "url_path", action),
            attrs=method.attrs if hasattr(method, "attrs") else None,
            icon=method.icon if hasattr(method, "icon") else None,
            variant=method.variant if hasattr(method, "variant") else None,
        )

    def get_actions_list(self, request: HttpRequest) -> list[UnfoldAction]:
        """
        Filters `actions_list` by permissions and returns list of UnfoldAction objects.
        """
        return self._filter_unfold_actions_by_permissions(
            request, self._get_base_actions_list()
        )

    def get_actions_detail(
        self, request: HttpRequest, object_id: int
    ) -> list[UnfoldAction]:
        """
        Filters `actions_detail` by permissions and returns list of UnfoldAction objects.
        """
        return self._filter_unfold_actions_by_permissions(
            request, self._get_base_actions_detail(), object_id
        )

    def get_actions_row(self, request: HttpRequest) -> list[UnfoldAction]:
        """
        Filters `actions_row` by permissions and returns list of UnfoldAction objects.
        """
        return self._filter_unfold_actions_by_permissions(
            request, self._get_base_actions_row()
        )

    def get_actions_submit_line(
        self, request: HttpRequest, object_id: int
    ) -> list[UnfoldAction]:
        """
        Filters `actions_submit_line` by permissions and returns list of UnfoldAction objects.
        """
        return self._filter_unfold_actions_by_permissions(
            request, self._get_base_actions_submit_line(), object_id
        )

    def _extract_action_names(self, actions: list[str | dict]) -> list[str]:
        """
        Gets the list of only actions names from the actions structure provided in ModelAdmin
        """
        results = []

        for action in actions or []:
            if isinstance(action, dict) and "items" in action:
                results.extend(action["items"])
            else:
                results.append(action)

        return results

    def _get_base_actions_list(self) -> list[UnfoldAction]:
        """
        Returns list of UnfoldAction objects for `actions_list`.
        """
        return [
            self.get_unfold_action(action)
            for action in self._extract_action_names(self.actions_list)
        ]

    def _get_base_actions_detail(self) -> list[UnfoldAction]:
        """
        Returns list of UnfoldAction objects for `actions_detail`.
        """
        return [
            self.get_unfold_action(action)
            for action in self._extract_action_names(self.actions_detail) or []
        ]

    def _get_base_actions_row(self) -> list[UnfoldAction]:
        """
        Returns list of UnfoldAction objects for `actions_row`.
        """
        return [
            self.get_unfold_action(action)
            for action in self._extract_action_names(self.actions_row) or []
        ]

    def _get_base_actions_submit_line(self) -> list[UnfoldAction]:
        """
        Returns list of UnfoldAction objects for `actions_submit_line`.
        """
        return [
            self.get_unfold_action(action)
            for action in self._extract_action_names(self.actions_submit_line) or []
        ]

    def _get_instance_method(self, method_name: str) -> Callable:
        """
        Searches for method on self instance based on method_name and returns it if it exists.
        If it does not exist or is not callable, it raises UnfoldException
        """
        try:
            method = getattr(self, method_name)
        except AttributeError as e:
            raise UnfoldException(
                f"Method {method_name} specified does not exist on current object"
            ) from e

        if not callable(method):
            raise UnfoldException(f"{method_name} is not callable")

        return method

    def _get_actions_navigation(
        self,
        provided_actions: list[str | dict],
        allowed_actions: list[UnfoldAction],
        object_id: str | None = None,
    ) -> list[str | dict]:
        """
        Builds navigation structure for the actions which is going to be provided to the template.
        """
        navigation = []

        def get_action_by_name(name: str) -> UnfoldAction:
            """
            Searches for an action in allowed_actions by its name.
            """
            for action in allowed_actions:
                full_action_name = (
                    f"{self.model._meta.app_label}_{self.model._meta.model_name}_{name}"
                )

                if action.action_name == full_action_name:
                    return action

        def get_action_path(action: UnfoldAction) -> str:
            """
            Returns the URL path for an action.
            """
            path_name = f"{self.admin_site.name}:{action.action_name}"

            if object_id:
                return reverse(path_name, args=(object_id,))

            return reverse(path_name)

        def get_action_attrs(action: UnfoldAction) -> dict:
            """
            Returns the attributes for an action which will be used in the template.
            """
            return {
                "title": action.description,
                "icon": action.icon,
                "variant": action.variant,
                "attrs": action.method.attrs,
                "path": get_action_path(action),
            }

        def build_dropdown(nav_item: dict) -> dict | None:
            """
            Builds a dropdown structure for the action.
            """
            dropdown = {
                "title": nav_item["title"],
                "icon": nav_item.get("icon"),
                "variant": nav_item.get("variant", ActionVariant.DEFAULT),
                "items": [],
            }

            for child in nav_item["items"]:
                if action := get_action_by_name(child):
                    dropdown["items"].append(get_action_attrs(action))

            if len(dropdown["items"]) > 0:
                return dropdown

        for nav_item in provided_actions:
            if isinstance(nav_item, str):
                if action := get_action_by_name(nav_item):
                    navigation.append(get_action_attrs(action))
            elif isinstance(nav_item, dict):
                if dropdown := build_dropdown(nav_item):
                    navigation.append(dropdown)

        return navigation

    def _filter_unfold_actions_by_permissions(
        self,
        request: HttpRequest,
        actions: list[UnfoldAction],
        object_id: int | str | None = None,
    ) -> list[UnfoldAction]:
        """
        Filters out actions that the user doesn't have access to.
        """
        filtered_actions = []

        for action in actions:
            if not hasattr(action.method, "allowed_permissions"):
                filtered_actions.append(action)
                continue

            permission_rules = []

            for permission in action.method.allowed_permissions:
                if "." in permission:
                    permission_rules.append(permission)
                else:
                    permission_rules.append(
                        getattr(self, f"has_{permission}_permission")
                    )

            permission_checks = []

            for permission_rule in permission_rules:
                if isinstance(permission_rule, str) and "." in permission_rule:
                    permission_checks.append(request.user.has_perm(permission_rule))
                elif object_id:
                    permission_checks.append(permission_rule(request, object_id))
                else:
                    permission_checks.append(permission_rule(request))

            if all(permission_checks):
                filtered_actions.append(action)

        return filtered_actions
