import copy
from functools import update_wrapper
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from django import forms
from django.contrib.admin import ModelAdmin as BaseModelAdmin
from django.contrib.admin import StackedInline as BaseStackedInline
from django.contrib.admin import TabularInline as BaseTabularInline
from django.contrib.admin import display, helpers
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.db import models
from django.db.models import BLANK_CHOICE_DASH, Model
from django.db.models.fields import Field
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.forms import Form
from django.forms.fields import TypedChoiceField
from django.forms.models import ModelChoiceField, ModelMultipleChoiceField
from django.forms.widgets import SelectMultiple
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import URLPattern, path, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views import View

from .checks import UnfoldModelAdminChecks
from .dataclasses import UnfoldAction
from .exceptions import UnfoldException
from .fields import UnfoldAdminField, UnfoldAdminReadonlyField
from .forms import ActionForm
from .typing import FieldsetsType
from .widgets import (
    SELECT_CLASSES,
    UnfoldAdminBigIntegerFieldWidget,
    UnfoldAdminDecimalFieldWidget,
    UnfoldAdminEmailInputWidget,
    UnfoldAdminFileFieldWidget,
    UnfoldAdminImageFieldWidget,
    UnfoldAdminImageSmallFieldWidget,
    UnfoldAdminIntegerFieldWidget,
    UnfoldAdminIntegerRangeWidget,
    UnfoldAdminMoneyWidget,
    UnfoldAdminNullBooleanSelectWidget,
    UnfoldAdminRadioSelectWidget,
    UnfoldAdminSelectWidget,
    UnfoldAdminSingleDateWidget,
    UnfoldAdminSingleTimeWidget,
    UnfoldAdminSplitDateTimeWidget,
    UnfoldAdminTextareaWidget,
    UnfoldAdminTextInputWidget,
    UnfoldAdminUUIDInputWidget,
    UnfoldBooleanSwitchWidget,
    UnfoldBooleanWidget,
    UnfoldForeignKeyRawIdWidget,
)

try:
    from django.contrib.postgres.fields import ArrayField, IntegerRangeField
    from django.contrib.postgres.search import SearchVectorField

    HAS_PSYCOPG = True
except ImportError:
    HAS_PSYCOPG = False

try:
    from djmoney.models.fields import MoneyField

    HAS_MONEY = True
except ImportError:
    HAS_MONEY = False

FORMFIELD_OVERRIDES = {
    models.DateTimeField: {
        "form_class": forms.SplitDateTimeField,
        "widget": UnfoldAdminSplitDateTimeWidget,
    },
    models.DateField: {"widget": UnfoldAdminSingleDateWidget},
    models.TimeField: {"widget": UnfoldAdminSingleTimeWidget},
    models.EmailField: {"widget": UnfoldAdminEmailInputWidget},
    models.CharField: {"widget": UnfoldAdminTextInputWidget},
    models.URLField: {"widget": UnfoldAdminTextInputWidget},
    models.GenericIPAddressField: {"widget": UnfoldAdminTextInputWidget},
    models.UUIDField: {"widget": UnfoldAdminUUIDInputWidget},
    models.TextField: {"widget": UnfoldAdminTextareaWidget},
    models.NullBooleanField: {"widget": UnfoldAdminNullBooleanSelectWidget},
    models.BooleanField: {"widget": UnfoldBooleanSwitchWidget},
    models.IntegerField: {"widget": UnfoldAdminIntegerFieldWidget},
    models.BigIntegerField: {"widget": UnfoldAdminBigIntegerFieldWidget},
    models.DecimalField: {"widget": UnfoldAdminDecimalFieldWidget},
    models.FloatField: {"widget": UnfoldAdminDecimalFieldWidget},
    models.FileField: {"widget": UnfoldAdminFileFieldWidget},
    models.ImageField: {"widget": UnfoldAdminImageFieldWidget},
    models.JSONField: {"widget": UnfoldAdminTextareaWidget},
    models.DurationField: {"widget": UnfoldAdminTextInputWidget},
}

if HAS_PSYCOPG:
    FORMFIELD_OVERRIDES.update(
        {
            ArrayField: {"widget": UnfoldAdminTextareaWidget},
            SearchVectorField: {"widget": UnfoldAdminTextareaWidget},
            IntegerRangeField: {"widget": UnfoldAdminIntegerRangeWidget},
        }
    )

if HAS_MONEY:
    FORMFIELD_OVERRIDES.update(
        {
            MoneyField: {"widget": UnfoldAdminMoneyWidget},
        }
    )

FORMFIELD_OVERRIDES_INLINE = copy.deepcopy(FORMFIELD_OVERRIDES)

FORMFIELD_OVERRIDES_INLINE.update(
    {
        models.ImageField: {"widget": UnfoldAdminImageSmallFieldWidget},
    }
)

checkbox = UnfoldBooleanWidget(
    {"class": "action-select", "aria-label": _("Select record")}, lambda value: False
)

helpers.AdminField = UnfoldAdminField

helpers.AdminReadonlyField = UnfoldAdminReadonlyField


class ModelAdminMixin:
    def __init__(self, model, admin_site):
        overrides = copy.deepcopy(FORMFIELD_OVERRIDES)

        for k, v in self.formfield_overrides.items():
            overrides.setdefault(k, {}).update(v)

        self.formfield_overrides = overrides

        super().__init__(model, admin_site)

    def formfield_for_choice_field(
        self, db_field: Field, request: HttpRequest, **kwargs
    ) -> TypedChoiceField:
        if "widget" not in kwargs:
            if db_field.name in self.radio_fields:
                kwargs["widget"] = UnfoldAdminRadioSelectWidget(
                    radio_style=self.radio_fields[db_field.name]
                )
            else:
                kwargs["widget"] = UnfoldAdminSelectWidget()

        if "choices" not in kwargs:
            kwargs["choices"] = db_field.get_choices(
                include_blank=db_field.blank, blank_choice=[("", _("Select value"))]
            )

        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def formfield_for_foreignkey(
        self, db_field: ForeignKey, request: HttpRequest, **kwargs
    ) -> Optional[ModelChoiceField]:
        db = kwargs.get("using")

        # Overrides widgets for all related fields
        if "widget" not in kwargs:
            if db_field.name in self.raw_id_fields:
                kwargs["widget"] = UnfoldForeignKeyRawIdWidget(
                    db_field.remote_field, self.admin_site, using=db
                )
            elif (
                db_field.name not in self.get_autocomplete_fields(request)
                and db_field.name not in self.radio_fields
            ):
                kwargs["widget"] = UnfoldAdminSelectWidget()
                kwargs["empty_label"] = _("Select value")

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(
        self,
        db_field: ManyToManyField,
        request: HttpRequest,
        **kwargs,
    ) -> ModelMultipleChoiceField:
        if "widget" not in kwargs:
            if db_field.name in self.raw_id_fields:
                kwargs["widget"] = UnfoldAdminTextInputWidget()

        form_field = super().formfield_for_manytomany(db_field, request, **kwargs)

        # If M2M uses intermediary model, form_field will be None
        if not form_field:
            return None

        if isinstance(form_field.widget, SelectMultiple):
            form_field.widget.attrs["class"] = " ".join(SELECT_CLASSES)

        return form_field

    def formfield_for_nullboolean_field(
        self, db_field: Field, request: HttpRequest, **kwargs
    ) -> Optional[Field]:
        if "widget" not in kwargs:
            kwargs["widget"] = UnfoldAdminNullBooleanSelectWidget()

        return db_field.formfield(**kwargs)

    def formfield_for_dbfield(
        self, db_field: Field, request: HttpRequest, **kwargs
    ) -> Optional[Field]:
        if isinstance(db_field, models.BooleanField) and db_field.null is True:
            return self.formfield_for_nullboolean_field(db_field, request, **kwargs)

        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)

        if formfield and isinstance(formfield.widget, RelatedFieldWidgetWrapper):
            formfield.widget.template_name = (
                "unfold/widgets/related_widget_wrapper.html"
            )

        return formfield


class ModelAdmin(ModelAdminMixin, BaseModelAdmin):
    action_form = ActionForm
    actions_list = ()
    actions_row = ()
    actions_detail = ()
    actions_submit_line = ()
    custom_urls = ()
    add_fieldsets = ()
    list_horizontal_scrollbar_top = False
    list_filter_submit = False
    list_fullwidth = False
    list_disable_select_all = False
    compressed_fields = False
    readonly_preprocess_fields = {}
    warn_unsaved_form = False
    checks_class = UnfoldModelAdminChecks

    @property
    def media(self):
        media = super().media
        additional_media = forms.Media()

        for filter in self.list_filter:
            if (
                isinstance(filter, (tuple, list))
                and hasattr(filter[1], "form_class")
                and hasattr(filter[1].form_class, "Media")
            ):
                additional_media += forms.Media(filter[1].form_class.Media)
            elif hasattr(filter, "form_class") and hasattr(filter.form_class, "Media"):
                additional_media += forms.Media(filter.form_class.Media)

        return media + additional_media

    def get_fieldsets(self, request: HttpRequest, obj=None) -> FieldsetsType:
        if not obj and self.add_fieldsets:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def _filter_unfold_actions_by_permissions(
        self,
        request: HttpRequest,
        actions: List[UnfoldAction],
        object_id: Optional[Union[int, str]] = None,
    ) -> List[UnfoldAction]:
        """Filter out any Unfold actions that the user doesn't have access to."""
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
                if any(
                    has_permission(request, object_id)
                    for has_permission in permission_checks
                ):
                    filtered_actions.append(action)
            else:
                if any(has_permission(request) for has_permission in permission_checks):
                    filtered_actions.append(action)

        return filtered_actions

    def get_actions_list(self, request: HttpRequest) -> List[UnfoldAction]:
        return self._filter_unfold_actions_by_permissions(
            request, self._get_base_actions_list()
        )

    def _get_base_actions_list(self) -> List[UnfoldAction]:
        """
        Returns all available list global actions, prior to any filtering
        """
        return [self.get_unfold_action(action) for action in self.actions_list or []]

    def get_actions_detail(
        self, request: HttpRequest, object_id: int
    ) -> List[UnfoldAction]:
        return self._filter_unfold_actions_by_permissions(
            request, self._get_base_actions_detail(), object_id
        )

    def _get_base_actions_detail(self) -> List[UnfoldAction]:
        """
        Returns all available detail actions, prior to any filtering
        """
        return [self.get_unfold_action(action) for action in self.actions_detail or []]

    def get_actions_row(self, request: HttpRequest) -> List[UnfoldAction]:
        return self._filter_unfold_actions_by_permissions(
            request, self._get_base_actions_row()
        )

    def _get_base_actions_row(self) -> List[UnfoldAction]:
        """
        Returns all available row actions, prior to any filtering
        """
        return [self.get_unfold_action(action) for action in self.actions_row or []]

    def get_actions_submit_line(
        self, request: HttpRequest, object_id: int
    ) -> List[UnfoldAction]:
        return self._filter_unfold_actions_by_permissions(
            request, self._get_base_actions_submit_line(), object_id
        )

    def _get_base_actions_submit_line(self) -> List[UnfoldAction]:
        """
        Returns all available submit row actions, prior to any filtering
        """
        return [
            self.get_unfold_action(action) for action in self.actions_submit_line or []
        ]

    def get_custom_urls(self) -> Tuple[Tuple[str, str, View], ...]:
        """
        Method to get custom views for ModelAdmin with their urls

        Format of custom_urls item:
            ("path_to_view", "name_of_view", view_itself)
        """
        return () if self.custom_urls is None else self.custom_urls

    def get_urls(self) -> List[URLPattern]:
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
                action.path,
                wrap(action.method),
                name=action.action_name,
            )
            for action in self._get_base_actions_list()
        ]

        action_detail_urls = [
            path(
                f"<path:object_id>/{action.path}/",
                wrap(action.method),
                name=action.action_name,
            )
            for action in self._get_base_actions_detail()
        ]

        action_row_urls = [
            path(
                f"<path:object_id>/{action.path}",
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

    def _path_from_custom_url(self, custom_url) -> URLPattern:
        # TODO: wrap()
        return path(
            custom_url[0],
            self.admin_site.admin_view(custom_url[2]),
            {"model_admin": self},
            name=custom_url[1],
        )

    def changeform_view(
        self,
        request: HttpRequest,
        object_id: Optional[str] = None,
        form_url: str = "",
        extra_context: Optional[Dict[str, bool]] = None,
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

    def changelist_view(
        self, request: HttpRequest, extra_context: Optional[Dict[str, str]] = None
    ) -> TemplateResponse:
        if extra_context is None:
            extra_context = {}

        actions = [
            {
                "title": action.description,
                "attrs": action.method.attrs,
                "path": reverse(f"{self.admin_site.name}:{action.action_name}"),
            }
            for action in self.get_actions_list(request)
        ]

        actions_row = [
            {
                "title": action.description,
                "attrs": action.method.attrs,
                "raw_path": f"{self.admin_site.name}:{action.action_name}",
            }
            for action in self.get_actions_row(request)
        ]

        extra_context.update({"actions_list": actions, "actions_row": actions_row})

        return super().changelist_view(request, extra_context)

    def get_unfold_action(self, action: str) -> UnfoldAction:
        """
        Converts action name to UnfoldAction
        :param action:
        :return:
        """
        method = self._get_instance_method(action)

        return UnfoldAction(
            action_name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_{action}",
            method=method,
            description=self._get_action_description(method, action),
            path=self._get_action_url(method, action),
            attrs=method.attrs if hasattr(method, "attrs") else None,
        )

    @staticmethod
    def _get_action_url(func: Callable, name: str) -> str:
        """
        Returns action URL if it was specified in @action decorator.
        If it was not, name of the action is returned.
        :param func:
        :param name:
        :return:
        """
        return getattr(func, "url_path", name)

    def save_model(
        self, request: HttpRequest, obj: Model, form: Form, change: Any
    ) -> None:
        super().save_model(request, obj, form, change)

        for action in self.get_actions_submit_line(request, obj.pk):
            if action.action_name not in request.POST:
                continue

            action.method(request, obj)

    def _get_instance_method(self, method_name: str) -> Callable:
        """
        Searches for method on self instance based on method_name and returns it if it exists.
        If it does not exist or is not callable, it raises UnfoldException
        :param method_name: Name of the method to search for
        :return: method from self instance
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

    def get_action_choices(
        self, request: HttpRequest, default_choices=BLANK_CHOICE_DASH
    ):
        default_choices = [("", _("Select action"))]
        return super().get_action_choices(request, default_choices)

    @display(description=mark_safe(checkbox.render("action_toggle_all", 1)))
    def action_checkbox(self, obj: Model):
        return checkbox.render(helpers.ACTION_CHECKBOX_NAME, str(obj.pk))

    def response_change(self, request: HttpRequest, obj: Model) -> HttpResponse:
        res = super().response_change(request, obj)
        if "next" in request.GET:
            return redirect(request.GET["next"])
        return res

    def response_add(
        self, request: HttpRequest, obj: Model, post_url_continue: Optional[str] = None
    ) -> HttpResponse:
        res = super().response_add(request, obj, post_url_continue)
        if "next" in request.GET:
            return redirect(request.GET["next"])
        return res


class TabularInline(ModelAdminMixin, BaseTabularInline):
    formfield_overrides = FORMFIELD_OVERRIDES_INLINE
    readonly_preprocess_fields = {}


class StackedInline(ModelAdminMixin, BaseStackedInline):
    formfield_overrides = FORMFIELD_OVERRIDES_INLINE
    readonly_preprocess_fields = {}
