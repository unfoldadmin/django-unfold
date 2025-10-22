from functools import update_wrapper
from typing import Any

from django import forms
from django.contrib.admin import ModelAdmin as BaseModelAdmin
from django.contrib.admin import StackedInline as BaseStackedInline
from django.contrib.admin import TabularInline as BaseTabularInline
from django.contrib.admin import display, helpers
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.contenttypes.admin import (
    GenericStackedInline as BaseGenericStackedInline,
)
from django.contrib.contenttypes.admin import (
    GenericTabularInline as BaseGenericTabularInline,
)
from django.db.models import BLANK_CHOICE_DASH, Model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import URLPattern, path
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views import View

from unfold.checks import UnfoldModelAdminChecks
from unfold.datasets import BaseDataset
from unfold.forms import (
    ActionForm,
    PaginationGenericInlineFormSet,
    PaginationInlineFormSet,
)
from unfold.mixins import (
    ActionModelAdminMixin,
    BaseModelAdminMixin,
    DatasetModelAdminMixin,
)
from unfold.overrides import FORMFIELD_OVERRIDES_INLINE
from unfold.typing import FieldsetsType
from unfold.views import ChangeList
from unfold.widgets import UnfoldBooleanWidget

checkbox = UnfoldBooleanWidget(
    {
        "class": "action-select",
        "aria-label": _("Select record"),
    },
    lambda value: False,
)


class ModelAdmin(
    BaseModelAdminMixin, ActionModelAdminMixin, DatasetModelAdminMixin, BaseModelAdmin
):
    action_form = ActionForm
    custom_urls = ()
    add_fieldsets = ()
    ordering_field = None
    hide_ordering_field = False
    list_horizontal_scrollbar_top = False
    list_filter_submit = False
    list_filter_sheet = True
    list_fullwidth = False
    list_disable_select_all = False
    list_before_template = None
    list_after_template = None
    change_form_before_template = None
    change_form_after_template = None
    change_form_outer_before_template = None
    change_form_outer_after_template = None
    change_form_datasets = ()
    compressed_fields = False
    readonly_preprocess_fields = {}
    warn_unsaved_form = False
    checks_class = UnfoldModelAdminChecks

    @property
    def media(self):
        if not hasattr(self, "request"):
            return super().media

        media = super().media

        for filter in self.get_list_filter(self.request):
            if (
                isinstance(filter, tuple | list)
                and hasattr(filter[1], "form_class")
                and hasattr(filter[1].form_class, "Media")
            ):
                media += forms.Media(filter[1].form_class.Media)
            elif hasattr(filter, "form_class") and hasattr(filter.form_class, "Media"):
                media += forms.Media(filter.form_class.Media)

        return media

    def changelist_view(
        self, request: HttpRequest, extra_context: dict[str, str] | None = None
    ) -> TemplateResponse:
        self.request = request

        if self.ordering_field and self.ordering_field not in self.list_editable:
            list_editable = list(getattr(self, "list_editable", []))
            list_editable.append(self.ordering_field)
            self.list_editable = list_editable

        return super().changelist_view(request, extra_context)

    def get_list_display(self, request: HttpRequest) -> list[str]:
        list_display = super().get_list_display(request)

        if self.ordering_field and self.ordering_field not in list_display:
            list_display.append(self.ordering_field)

        return list_display

    def get_fieldsets(
        self, request: HttpRequest, obj: Model | None = None
    ) -> FieldsetsType:
        if not obj and self.add_fieldsets:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_custom_urls(self) -> tuple[tuple[str, str, View], ...]:
        """
        Method to get custom views for ModelAdmin with their urls

        Format of custom_urls item:
            ("path_to_view", "name_of_view", view_itself)
        """
        return () if self.custom_urls is None else self.custom_urls

    def get_urls(self) -> list[URLPattern]:
        urls = super().get_urls()

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        custom_urls = [
            self._path_from_custom_url(custom_url)
            for custom_url in self.get_custom_urls()
        ]

        actions_list_urls = [
            path(
                f"{action.path.removesuffix('/')}/",
                wrap(action.method),
                name=action.action_name,
            )
            for action in self._get_base_actions_list()
        ]

        action_detail_urls = [
            path(
                f"<path:object_id>/{action.path.removesuffix('/')}/",
                wrap(action.method),
                name=action.action_name,
            )
            for action in self._get_base_actions_detail()
        ]

        action_row_urls = [
            path(
                f"<path:object_id>/{action.path.removesuffix('/')}/",
                wrap(action.method),
                name=action.action_name,
            )
            for action in self._get_base_actions_row()
        ]

        return (
            custom_urls
            + action_row_urls
            + actions_list_urls
            + action_detail_urls
            + urls
        )

    def _path_from_custom_url(self, custom_url: tuple[str, str, View]) -> URLPattern:
        return path(
            custom_url[0],
            self.admin_site.admin_view(custom_url[2]),
            {"model_admin": self},
            name=custom_url[1],
        )

    def get_action_choices(
        self,
        request: HttpRequest,
        default_choices: list[tuple[str, str]] = BLANK_CHOICE_DASH,
    ) -> list[tuple[str, str]]:
        default_choices = [("", _("Select action"))]
        return super().get_action_choices(request, default_choices)

    @display(description=mark_safe(checkbox.render("action_toggle_all", 1)))
    def action_checkbox(self, obj: Model) -> str:
        return checkbox.render(helpers.ACTION_CHECKBOX_NAME, str(obj.pk))

    def response_change(self, request: HttpRequest, obj: Model) -> HttpResponse:
        res = super().response_change(request, obj)
        if "next" in request.GET:
            return redirect(request.GET["next"])
        return res

    def response_add(
        self, request: HttpRequest, obj: Model, post_url_continue: str | None = None
    ) -> HttpResponse:
        res = super().response_add(request, obj, post_url_continue)
        if "next" in request.GET:
            return redirect(request.GET["next"])
        return res

    def get_changelist(self, request: HttpRequest, **kwargs: Any) -> ChangeList:
        return ChangeList

    def get_formset_kwargs(
        self, request: HttpRequest, obj: Model, inline: InlineModelAdmin, prefix: str
    ) -> dict[str, Any]:
        formset_kwargs = super().get_formset_kwargs(request, obj, inline, prefix)

        if hasattr(inline, "per_page") and inline.per_page:
            formset_kwargs["request"] = request
            formset_kwargs["per_page"] = inline.per_page

        return formset_kwargs

    def get_changeform_datasets(self, request: HttpRequest) -> list[type[BaseDataset]]:
        return self.change_form_datasets


class BaseInlineMixin:
    formfield_overrides = FORMFIELD_OVERRIDES_INLINE
    readonly_preprocess_fields = {}
    ordering_field = None
    per_page = None
    hide_ordering_field = False
    collapsible = False


class TabularInline(BaseInlineMixin, BaseModelAdminMixin, BaseTabularInline):
    formset = PaginationInlineFormSet


class StackedInline(BaseInlineMixin, BaseModelAdminMixin, BaseStackedInline):
    formset = PaginationInlineFormSet


class GenericStackedInline(
    BaseInlineMixin, BaseModelAdminMixin, BaseGenericStackedInline
):
    formset = PaginationGenericInlineFormSet


class GenericTabularInline(
    BaseInlineMixin, BaseModelAdminMixin, BaseGenericTabularInline
):
    formset = PaginationGenericInlineFormSet
