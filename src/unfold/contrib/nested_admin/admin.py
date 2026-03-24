from __future__ import annotations

from typing import Any, cast

from django.apps import apps
from django.contrib.admin.utils import quote
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.core import checks
from django.core.exceptions import (
    FieldDoesNotExist,
    ImproperlyConfigured,
    PermissionDenied,
)
from django.db import models
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBase,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404
from django.urls import Resolver404, path, resolve, reverse
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _


def _lock_related_widget(widget: object) -> None:
    if not isinstance(widget, RelatedFieldWidgetWrapper):
        return

    widget.can_add_related = False
    widget.can_change_related = False
    widget.can_delete_related = False


class NestedChildAdminMixin:
    nested_parent_fk: str | None = None

    def _parent_relation_field(self) -> models.Field:
        field = self.model._meta.get_field(self._parent_fk_name())

        if field.remote_field is None:
            raise ImproperlyConfigured("nested_parent_fk must reference a parent model")

        return field

    def _parent_fk_name(self) -> str:
        if self.nested_parent_fk is not None:
            return self.nested_parent_fk

        return "parent"

    def _parent_model_meta(self) -> models.options.Options:
        return self._parent_relation_field().remote_field.model._meta

    def _nested_url_name(self, kind: str) -> str:
        parent_meta = self._parent_model_meta()
        child_meta = self.model._meta
        return f"{parent_meta.app_label}_{parent_meta.model_name}_{child_meta.model_name}_{kind}"

    def _nested_child_url(self, kind: str, parent_id: str, *extra_args: object) -> str:
        return reverse(
            f"{self.admin_site.name}:{self._nested_url_name(kind)}",
            args=[parent_id, *extra_args],
        )

    def _plain_child_url(self, kind: str, *args: object) -> str:
        child_meta = self.model._meta
        return reverse(
            f"{self.admin_site.name}:{child_meta.app_label}_{child_meta.model_name}_{kind}",
            args=args,
        )

    def get_parent_id(
        self, request: HttpRequest, *, obj: models.Model | None = None
    ) -> str | None:
        parent_id = getattr(request, "nested_parent_id", None)
        if isinstance(parent_id, str):
            return parent_id

        resolver_match = request.resolver_match
        if resolver_match is not None:
            parent_id = resolver_match.kwargs.get("parent_id")
            if isinstance(parent_id, str):
                return parent_id

        fk_name = self._parent_fk_name()

        for key in (fk_name, f"{fk_name}__id__exact"):
            parent_id = request.GET.get(key)
            if parent_id:
                return parent_id

            parent_id = request.POST.get(key)
            if parent_id:
                return parent_id

        if obj is None:
            return None

        return self._parent_id_from_obj(obj)

    def get_parent_object(
        self, request: HttpRequest, *, obj: models.Model | None = None
    ) -> models.Model | None:
        parent_object = getattr(request, "nested_parent_object", None)
        if isinstance(parent_object, models.Model):
            return parent_object

        parent_id = self.get_parent_id(request, obj=obj)
        if parent_id is None:
            return None

        return (
            self._parent_relation_field()
            .remote_field.model._default_manager.filter(pk=parent_id)
            .first()
        )

    def get_nested_url(
        self,
        request: HttpRequest,
        kind: str,
        *extra_args: object,
        obj: models.Model | None = None,
    ) -> str | None:
        parent_id = self.get_parent_id(request, obj=obj)
        if parent_id is None:
            return None

        return self._nested_child_url(kind, parent_id, *extra_args)

    def get_change_url(
        self,
        request: HttpRequest,
        object_id: object,
        *,
        obj: models.Model | None = None,
    ) -> str:
        nested_change_url = self.get_nested_url(request, "change", object_id, obj=obj)
        if nested_change_url is not None:
            return nested_change_url

        return self._plain_child_url("change", object_id)

    def _parent_id_from_obj(self, obj: models.Model) -> str | None:
        parent_id = self._parent_relation_field().value_from_object(obj)
        if parent_id is None:
            return None

        return str(parent_id)

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        initial = super().get_changeform_initial_data(request)
        parent_id = self.get_parent_id(request)
        if parent_id is not None:
            initial[self._parent_fk_name()] = parent_id
        return initial

    def formfield_for_foreignkey(
        self, db_field: models.Field, request: HttpRequest, **kwargs: Any
    ):
        if db_field.name != self._parent_fk_name():
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

        parent_id = self.get_parent_id(request)
        if parent_id is None:
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

        remote_field = db_field.remote_field
        if remote_field is None:
            raise ImproperlyConfigured("nested_parent_fk must reference a parent model")
        kwargs["queryset"] = remote_field.model._default_manager.filter(pk=parent_id)
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)

        if formfield is not None:
            _lock_related_widget(formfield.widget)

        return formfield

    def _append_preserved_filters(self, request: HttpRequest, url: str) -> str:
        preserved = self.get_preserved_filters(request)
        if preserved:
            separator = "&" if "?" in url else "?"
            return f"{url}{separator}{preserved.lstrip('?')}"

        return url

    def delete_view(
        self,
        request: HttpRequest,
        object_id: str,
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        parent_id_before: str | None = None
        obj = self.get_object(request, object_id)
        if obj is not None:
            parent_id_before = self._parent_id_from_obj(obj)

        response = super().delete_view(request, object_id, extra_context=extra_context)

        if not isinstance(response, HttpResponseRedirect) or parent_id_before is None:
            return response

        changelist_url = self._nested_child_url("changelist", parent_id_before)
        return HttpResponseRedirect(
            self._append_preserved_filters(request, changelist_url)
        )

    def response_add(
        self,
        request: HttpRequest,
        obj: models.Model,
        post_url_continue: str | None = None,
    ) -> HttpResponse:
        parent_id = self.get_parent_id(request, obj=obj)
        if parent_id is None:
            return super().response_add(request, obj, post_url_continue)

        if "_addanother" in request.POST:
            add_url = self._nested_child_url("add", parent_id)
            return HttpResponseRedirect(
                self._append_preserved_filters(request, add_url)
            )

        change_url = self._nested_child_url("change", parent_id, obj.pk)
        return HttpResponseRedirect(self._append_preserved_filters(request, change_url))

    def response_change(self, request: HttpRequest, obj: models.Model) -> HttpResponse:
        parent_id = self.get_parent_id(request, obj=obj)
        if parent_id is None:
            return super().response_change(request, obj)

        if "_continue" in request.POST or "_saveasnew" in request.POST:
            change_url = self._nested_child_url("change", parent_id, obj.pk)
            return HttpResponseRedirect(
                self._append_preserved_filters(request, change_url)
            )

        if "_addanother" in request.POST:
            add_url = self._nested_child_url("add", parent_id)
            return HttpResponseRedirect(
                self._append_preserved_filters(request, add_url)
            )

        changelist_url = self._nested_child_url("changelist", parent_id)
        return HttpResponseRedirect(
            self._append_preserved_filters(request, changelist_url)
        )

    def response_delete(
        self, request: HttpRequest, obj_display: str, obj_id: str
    ) -> HttpResponse:
        parent_id = self.get_parent_id(request)
        if parent_id is None:
            return super().response_delete(request, obj_display, obj_id)

        changelist_url = self._nested_child_url("changelist", parent_id)
        return HttpResponseRedirect(
            self._append_preserved_filters(request, changelist_url)
        )

    def get_changelist(self, request: HttpRequest, **kwargs: Any):
        base_changelist = super().get_changelist(request, **kwargs)
        filter_key = f"{self._parent_fk_name()}__id__exact"

        class NestedChangeList(base_changelist):  # type: ignore[misc, valid-type]
            def __init__(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
                super().__init__(request, *args, **kwargs)
                self._nested_base_path = request.path
                self._is_nested_scoped = filter_key in self.params

                if self._is_nested_scoped:
                    self.add_url = f"{self._nested_base_path}add/"

            def url_for_result(self, result: models.Model) -> str:
                if not self._is_nested_scoped:
                    return super().url_for_result(result)

                return f"{self._nested_base_path}{quote(result.pk)}/change/"

        return NestedChangeList


class NestedParentAdminMixin:
    nested_child_model: type[models.Model] | None = None
    nested_child_fk_name: str = "parent"
    nested_segment: str | None = None
    nested_child_action_icon: str = "list"

    def _app_label(self) -> str:
        return cast("str", self.model._meta.app_label)

    def _parent_model_name(self) -> str:
        return cast("str", self.model._meta.model_name)

    def _child_model_name(self) -> str:
        return cast("str", self._child_model()._meta.model_name)

    def _segment(self) -> str:
        if self.nested_segment is not None:
            return self.nested_segment

        return self._child_model_name()

    def _base_nested_url_name(self) -> str:
        return f"{self._app_label()}_{self._parent_model_name()}_{self._child_model_name()}"

    def _nested_url_name(self, kind: str) -> str:
        return f"{self._base_nested_url_name()}_{kind}"

    def _admin_ns(self, name: str) -> str:
        return f"{self.admin_site.name}:{name}"

    def _child_model(self) -> type[models.Model]:
        if self.nested_child_model is None:
            raise ImproperlyConfigured("nested_child_model must be set")

        return self.nested_child_model

    def _child_admin(self) -> Any:
        child_model = self._child_model()

        if child_model not in self.admin_site._registry:
            raise ImproperlyConfigured(
                f"{child_model} is not registered with this AdminSite"
            )

        return self.admin_site._registry[child_model]

    def _force_parent_filter(
        self, request: HttpRequest, parent_id: str, *, mode: str = "changelist"
    ) -> HttpRequest:
        query_dict = request.GET.copy()
        query_dict[f"{self.nested_child_fk_name}__id__exact"] = parent_id

        if mode != "changelist":
            query_dict[self.nested_child_fk_name] = parent_id

        request.GET = cast("Any", query_dict)
        request.META["QUERY_STRING"] = query_dict.urlencode()
        return request

    def _set_nested_request_context(
        self,
        request: HttpRequest,
        parent: models.Model,
    ) -> HttpRequest:
        request.nested_parent_id = str(parent.pk)
        request.nested_parent_object = parent
        return request

    def _parent_change_url(self, parent_id: object) -> str:
        return reverse(
            self._admin_ns(f"{self._app_label()}_{self._parent_model_name()}_change"),
            args=[parent_id],
        )

    def _nested_child_url(
        self, kind: str, parent_id: object, *extra_args: object
    ) -> str:
        return reverse(
            self._admin_ns(self._nested_url_name(kind)),
            args=[parent_id, *extra_args],
        )

    def _nested_breadcrumbs(
        self,
        parent: models.Model,
        *,
        include_child_changelist: bool,
        child: models.Model | None = None,
    ) -> list[dict[str, str]]:
        app_label = self._app_label()
        breadcrumbs = [
            {
                "title": str(capfirst(apps.get_app_config(app_label).verbose_name)),
                "url": reverse(
                    f"{self.admin_site.name}:app_list",
                    kwargs={"app_label": app_label},
                ),
            },
            {
                "title": str(parent),
                "url": self._parent_change_url(parent.pk),
            },
        ]

        if include_child_changelist:
            child_model = self._child_model()
            breadcrumbs.append(
                {
                    "title": str(capfirst(child_model._meta.verbose_name_plural)),
                    "url": self._nested_child_url("changelist", parent.pk),
                }
            )

        if child is not None:
            breadcrumbs.append(
                {
                    "title": str(child),
                    "url": self._nested_child_change_url(parent, child),
                }
            )

        return breadcrumbs

    def _nested_child_changelist_url(self, parent: models.Model) -> str:
        return self._nested_child_url("changelist", parent.pk)

    def _nested_child_add_url(self, parent: models.Model) -> str:
        return self._nested_child_url("add", parent.pk)

    def _nested_child_change_url(
        self, parent: models.Model, child: models.Model
    ) -> str:
        return self._nested_child_url("change", parent.pk, child.pk)

    def _nested_child_history_url(
        self, parent: models.Model, child: models.Model
    ) -> str:
        return self._nested_child_url("history", parent.pk, child.pk)

    def _nested_child_delete_url(
        self, parent: models.Model, child: models.Model
    ) -> str:
        return self._nested_child_url("delete", parent.pk, child.pk)

    def _nested_child_action_proxy_url(
        self, parent: models.Model, child: models.Model, action_path: str
    ) -> str:
        return self._nested_child_url("action_proxy", parent.pk, child.pk, action_path)

    def _get_parent_or_404(self, parent_id: str) -> models.Model:
        return get_object_or_404(self.model, pk=parent_id)

    def _get_child_or_404(self, parent_id: str, object_id: str) -> models.Model:
        return get_object_or_404(
            self._child_model(),
            pk=object_id,
            **{f"{self.nested_child_fk_name}_id": parent_id},
        )

    def get_nested_object_tools(
        self, request: HttpRequest, parent: models.Model
    ) -> list[dict[str, str]]:
        child_admin = self._child_admin()

        if not child_admin.has_view_or_change_permission(request):
            return []

        child_model = self._child_model()
        return [
            {
                "title": str(capfirst(child_model._meta.verbose_name_plural)),
                "link": self._nested_child_changelist_url(parent),
                "icon": self.nested_child_action_icon,
            }
        ]

    def _nested_child_context(
        self,
        parent: models.Model,
        *,
        current_title: str,
        include_child_changelist: bool,
        back_url: str,
        child: models.Model | None = None,
    ) -> dict[str, Any]:
        breadcrumb_child = None
        if child is not None and current_title != str(child):
            breadcrumb_child = child

        context: dict[str, Any] = {
            "nested_add_url": self._nested_child_add_url(parent),
            "nested_back_url": back_url,
            "nested_breadcrumbs": self._nested_breadcrumbs(
                parent,
                include_child_changelist=include_child_changelist,
                child=breadcrumb_child,
            ),
            "nested_changelist_url": self._nested_child_changelist_url(parent),
            "nested_current_title": current_title,
        }

        if child is not None:
            context["nested_change_url"] = self._nested_child_change_url(parent, child)
            context["nested_delete_url"] = self._nested_child_delete_url(parent, child)
            context["nested_history_url"] = self._nested_child_history_url(
                parent, child
            )

        return context

    def _rewrite_nested_detail_actions(
        self,
        response: HttpResponseBase,
        parent: models.Model,
        child: models.Model,
    ) -> None:
        if not hasattr(response, "context_data"):
            return

        context_data = response.context_data
        actions_detail = context_data.get("actions_detail")
        if not isinstance(actions_detail, list):
            return

        plain_prefix = (
            reverse(
                f"{self.admin_site.name}:{child._meta.app_label}_{child._meta.model_name}_changelist"
            )
            + f"{child.pk}/"
        )

        def rewrite(actions: list[dict[str, Any]]) -> None:
            for action in actions:
                if "items" in action:
                    rewrite(action["items"])
                    continue

                path = action.get("path")
                if not isinstance(path, str) or not path.startswith(plain_prefix):
                    continue

                action["path"] = self._nested_child_action_proxy_url(
                    parent,
                    child,
                    path.removeprefix(plain_prefix),
                )

        rewrite(actions_detail)

    def get_urls(self):
        self._child_model()
        urls = super().get_urls()
        segment = self._segment()

        nested_urls = [
            path(
                f"<str:parent_id>/{segment}/",
                self.admin_site.admin_view(self.child_changelist_view),
                name=self._nested_url_name("changelist"),
            ),
            path(
                f"<str:parent_id>/{segment}/add/",
                self.admin_site.admin_view(self.child_add_view),
                name=self._nested_url_name("add"),
            ),
            path(
                f"<str:parent_id>/{segment}/<str:object_id>/change/",
                self.admin_site.admin_view(self.child_change_view),
                name=self._nested_url_name("change"),
            ),
            path(
                f"<str:parent_id>/{segment}/<str:object_id>/history/",
                self.admin_site.admin_view(self.child_history_view),
                name=self._nested_url_name("history"),
            ),
            path(
                f"<str:parent_id>/{segment}/<str:object_id>/delete/",
                self.admin_site.admin_view(self.child_delete_view),
                name=self._nested_url_name("delete"),
            ),
            path(
                f"<str:parent_id>/{segment}/<str:object_id>/actions/<path:action_path>",
                self.admin_site.admin_view(self.child_action_view),
                name=f"{self._base_nested_url_name()}_action_proxy",
            ),
            path(
                f"<str:parent_id>/{segment}/<str:object_id>/",
                self.admin_site.admin_view(self.child_change_redirect_view),
                name=f"{self._base_nested_url_name()}_{segment}_compat_change_nochange",
            ),
        ]

        return nested_urls + urls

    def child_changelist_view(
        self, request: HttpRequest, parent_id: str, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        parent = self._get_parent_or_404(parent_id)
        if not self.has_view_permission(request, obj=parent):
            raise PermissionDenied

        child_admin = self._child_admin()
        if not child_admin.has_view_or_change_permission(request):
            raise PermissionDenied

        request = self._set_nested_request_context(request, parent)
        request = self._force_parent_filter(request, parent_id, mode="changelist")
        child_model = self._child_model()
        extra_context = self._nested_child_context(
            parent,
            current_title=str(capfirst(child_model._meta.verbose_name_plural)),
            include_child_changelist=False,
            back_url=self._parent_change_url(parent.pk),
        )
        return child_admin.changelist_view(request, extra_context=extra_context)

    def changeform_view(
        self,
        request: HttpRequest,
        object_id: str | None = None,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        extra_context = extra_context or {}

        if object_id is not None:
            parent = self.get_object(request, object_id)
            if parent is not None and self.has_view_permission(request, obj=parent):
                extra_context["nested_object_tools"] = self.get_nested_object_tools(
                    request, parent
                )

        return super().changeform_view(request, object_id, form_url, extra_context)

    def child_add_view(
        self, request: HttpRequest, parent_id: str, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        parent = self._get_parent_or_404(parent_id)
        if not self.has_view_permission(request, obj=parent):
            raise PermissionDenied

        child_admin = self._child_admin()
        if not child_admin.has_add_permission(request):
            raise PermissionDenied

        request = self._set_nested_request_context(request, parent)
        request = self._force_parent_filter(request, parent_id, mode="add")
        child_model = self._child_model()
        extra_context = self._nested_child_context(
            parent,
            current_title=str(
                _("Add %(name)s") % {"name": capfirst(child_model._meta.verbose_name)}
            ),
            include_child_changelist=True,
            back_url=self._nested_child_changelist_url(parent),
        )
        return child_admin.add_view(request, extra_context=extra_context)

    def child_change_view(
        self,
        request: HttpRequest,
        parent_id: str,
        object_id: str,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        parent = self._get_parent_or_404(parent_id)
        child = self._get_child_or_404(parent_id, object_id)

        if not self.has_view_permission(request, obj=parent):
            raise PermissionDenied

        child_admin = self._child_admin()
        if not child_admin.has_view_or_change_permission(request, obj=child):
            raise PermissionDenied

        request = self._set_nested_request_context(request, parent)
        request = self._force_parent_filter(request, parent_id, mode="change")
        extra_context = self._nested_child_context(
            parent,
            current_title=str(child),
            include_child_changelist=True,
            back_url=self._nested_child_changelist_url(parent),
            child=child,
        )
        response = child_admin.change_view(
            request, object_id, extra_context=extra_context
        )
        self._rewrite_nested_detail_actions(response, parent, child)
        return response

    def child_history_view(
        self,
        request: HttpRequest,
        parent_id: str,
        object_id: str,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        parent = self._get_parent_or_404(parent_id)
        child = self._get_child_or_404(parent_id, object_id)
        if not self.has_view_permission(request, obj=parent):
            raise PermissionDenied

        child_admin = self._child_admin()
        if not child_admin.has_view_or_change_permission(request, obj=child):
            raise PermissionDenied

        request = self._set_nested_request_context(request, parent)
        request = self._force_parent_filter(request, parent_id, mode="change")
        extra_context = self._nested_child_context(
            parent,
            current_title=str(_("History")),
            include_child_changelist=True,
            back_url=self._nested_child_change_url(parent, child),
            child=child,
        )
        return child_admin.history_view(request, object_id, extra_context=extra_context)

    def child_delete_view(
        self,
        request: HttpRequest,
        parent_id: str,
        object_id: str,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        parent = self._get_parent_or_404(parent_id)
        child = self._get_child_or_404(parent_id, object_id)
        if not self.has_view_permission(request, obj=parent):
            raise PermissionDenied

        child_admin = self._child_admin()
        if not child_admin.has_delete_permission(request, obj=child):
            raise PermissionDenied

        request = self._set_nested_request_context(request, parent)
        request = self._force_parent_filter(request, parent_id, mode="change")
        extra_context = self._nested_child_context(
            parent,
            current_title=str(_("Delete")),
            include_child_changelist=True,
            back_url=self._nested_child_change_url(parent, child),
            child=child,
        )
        extra_context["nested_cancel_url"] = self._nested_child_change_url(
            parent, child
        )
        return child_admin.delete_view(request, object_id, extra_context=extra_context)

    def child_action_view(
        self,
        request: HttpRequest,
        parent_id: str,
        object_id: str,
        action_path: str,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        parent = self._get_parent_or_404(parent_id)
        child = self._get_child_or_404(parent_id, object_id)

        if not self.has_view_permission(request, obj=parent):
            raise PermissionDenied

        child_admin = self._child_admin()
        if not child_admin.has_view_or_change_permission(request, obj=child):
            raise PermissionDenied

        request = self._set_nested_request_context(request, parent)
        request = self._force_parent_filter(request, parent_id, mode="change")
        child_model = self._child_model()
        child_changelist_url = reverse(
            f"{self.admin_site.name}:{child_model._meta.app_label}_{child_model._meta.model_name}_changelist"
        )
        resolved_path = f"{child_changelist_url}{object_id}/{action_path}"

        try:
            match = resolve(resolved_path)
        except Resolver404 as err:
            raise Http404(f"Action not found: {action_path}") from err

        return match.func(request, *match.args, **match.kwargs)

    def child_change_redirect_view(
        self,
        request: HttpRequest,
        parent_id: str,
        object_id: str,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        return HttpResponseRedirect(
            reverse(
                self._admin_ns(self._nested_url_name("change")),
                args=[parent_id, object_id],
            )
        )

    def check(self, **kwargs: Any) -> list[checks.CheckMessage]:
        errors = list(super().check(**kwargs))
        errors.extend(self._check_nested_config())
        return errors

    def _check_nested_config(self) -> list[checks.CheckMessage]:
        if self.nested_child_model is None:
            return [
                checks.Error(
                    "nested_child_model must be set.",
                    obj=self.__class__,
                    id="nested_admin.E001",
                )
            ]

        try:
            field = self.nested_child_model._meta.get_field(self.nested_child_fk_name)
        except FieldDoesNotExist:
            return [
                checks.Error(
                    f"'{self.nested_child_fk_name}' is not a field on {self.nested_child_model.__name__}.",
                    obj=self.__class__,
                    id="nested_admin.E002",
                )
            ]

        errors: list[checks.CheckMessage] = []

        if not (field.many_to_one or field.one_to_one):
            errors.append(
                checks.Error(
                    f"'{self.nested_child_fk_name}' must be a ForeignKey/OneToOne to {self.model.__name__}.",
                    obj=self.__class__,
                    id="nested_admin.E003",
                )
            )
        elif field.remote_field is not None and field.remote_field.model != self.model:
            errors.append(
                checks.Error(
                    f"'{self.nested_child_fk_name}' points to {field.remote_field.model.__name__}, "
                    f"but parent admin is {self.model.__name__}.",
                    obj=self.__class__,
                    id="nested_admin.E004",
                )
            )

        return errors
