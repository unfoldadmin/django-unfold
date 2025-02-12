from typing import Any, Callable, Optional, Union

from django.db.models import Model
from django.forms import Form
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.urls import reverse

from unfold.dataclasses import UnfoldAction
from unfold.exceptions import UnfoldException


class ActionModelAdminMixin:
    def changelist_view(
        self, request: HttpRequest, extra_context: Optional[dict[str, str]] = None
    ) -> TemplateResponse:
        if extra_context is None:
            extra_context = {}

        actions_row = [
            {
                "title": action.description,
                "attrs": action.method.attrs,
                "raw_path": f"{self.admin_site.name}:{action.action_name}",
            }
            for action in self.get_actions_row(request)
        ]

        extra_context.update(
            {
                "actions_list": self._get_actions_navigation(
                    self.actions_list or [], self.get_actions_list(request)
                ),
                "actions_row": actions_row,
            }
        )

        return super().changelist_view(request, extra_context)

    def changeform_view(
        self,
        request: HttpRequest,
        object_id: Optional[str] = None,
        form_url: str = "",
        extra_context: Optional[dict[str, bool]] = None,
    ) -> Any:
        if extra_context is None:
            extra_context = {}

        actions = []
        if object_id:
            for action in self.get_actions_detail(request, object_id):
                actions.append(
                    {
                        "title": action.description,
                        "attrs": action.method.attrs,
                        "path": reverse(
                            f"{self.admin_site.name}:{action.action_name}",
                            args=(object_id,),
                        ),
                    }
                )

        extra_context.update(
            {
                "actions_submit_line": self.get_actions_submit_line(request, object_id),
                "actions_detail": actions,
            }
        )

        return super().changeform_view(request, object_id, form_url, extra_context)

    def save_model(
        self, request: HttpRequest, obj: Model, form: Form, change: Any
    ) -> None:
        super().save_model(request, obj, form, change)

        for action in self.get_actions_submit_line(request, obj.pk):
            if action.action_name not in request.POST:
                continue

            action.method(request, obj)

    def get_unfold_action(self, action: str) -> UnfoldAction:
        method = self._get_instance_method(action)

        return UnfoldAction(
            action_name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_{action}",
            method=method,
            description=self._get_action_description(method, action),
            path=getattr(method, "url_path", action),
            attrs=method.attrs if hasattr(method, "attrs") else None,
        )

    def get_actions_list(self, request: HttpRequest) -> list[UnfoldAction]:
        return self._filter_unfold_actions_by_permissions(
            request, self._get_base_actions_list()
        )

    def get_actions_detail(
        self, request: HttpRequest, object_id: int
    ) -> list[UnfoldAction]:
        return self._filter_unfold_actions_by_permissions(
            request, self._get_base_actions_detail(), object_id
        )

    def get_actions_row(self, request: HttpRequest) -> list[UnfoldAction]:
        return self._filter_unfold_actions_by_permissions(
            request, self._get_base_actions_row()
        )

    def get_actions_submit_line(
        self, request: HttpRequest, object_id: int
    ) -> list[UnfoldAction]:
        return self._filter_unfold_actions_by_permissions(
            request, self._get_base_actions_submit_line(), object_id
        )

    def _extract_action_names(self, actions: list[Union[str, dict]]) -> list[str]:
        results = []

        for action in actions or []:
            if isinstance(action, dict) and "items" in action:
                results.extend(action["items"])
            else:
                results.append(action)

        return results

    def _get_base_actions_list(self) -> list[UnfoldAction]:
        return [
            self.get_unfold_action(action)
            for action in self._extract_action_names(self.actions_list)
        ]

    def _get_base_actions_detail(self) -> list[UnfoldAction]:
        return [
            self.get_unfold_action(action)
            for action in self._extract_action_names(self.actions_detail) or []
        ]

    def _get_base_actions_row(self) -> list[UnfoldAction]:
        return [
            self.get_unfold_action(action)
            for action in self._extract_action_names(self.actions_row) or []
        ]

    def _get_base_actions_submit_line(self) -> list[UnfoldAction]:
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
        self, hierarchy: list[Union[str, dict]], actions: list[UnfoldAction]
    ) -> list[Union[str, dict]]:
        # TODO: test
        navigation = []

        def get_action_by_name(name: str) -> UnfoldAction:
            for action in actions:
                full_action_name = (
                    f"{self.model._meta.app_label}_{self.model._meta.model_name}_{name}"
                )
                if action.action_name == full_action_name:
                    return action

        for item in hierarchy:
            if isinstance(item, str) and (action := get_action_by_name(item)):
                navigation.append(
                    {
                        "title": action.description,
                        "attrs": action.method.attrs,
                        "path": reverse(f"{self.admin_site.name}:{action.action_name}"),
                    }
                )
            elif isinstance(item, dict):
                dropdown = {
                    "title": item["title"],
                    "items": [],
                }

                for child in item["items"]:
                    if action := get_action_by_name(child):
                        dropdown["items"].append(
                            {
                                "title": action.description,
                                "attrs": action.method.attrs,
                                "path": reverse(
                                    f"{self.admin_site.name}:{action.action_name}"
                                ),
                            }
                        )

                if len(dropdown["items"]) > 0:
                    navigation.append(dropdown)

        return navigation

    def _filter_unfold_actions_by_permissions(
        self,
        request: HttpRequest,
        actions: list[UnfoldAction],
        object_id: Optional[Union[int, str]] = None,
    ) -> list[UnfoldAction]:
        """
        Filters out actions that the user doesn't have access to.
        """
        filtered_actions = []
        for action in actions:
            if not hasattr(action.method, "allowed_permissions"):
                filtered_actions.append(action)
                continue

            permission_checks = (
                getattr(self, f"has_{permission}_permission")
                for permission in action.method.allowed_permissions
            )

            if object_id:
                if all(
                    has_permission(request, object_id)
                    for has_permission in permission_checks
                ):
                    filtered_actions.append(action)
            else:
                if all(has_permission(request) for has_permission in permission_checks):
                    filtered_actions.append(action)

        return filtered_actions
