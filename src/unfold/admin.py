import copy
from functools import update_wrapper

from django import forms
from django.contrib.admin import ModelAdmin as BaseModelAdmin
from django.contrib.admin import StackedInline as BaseStackedInline
from django.contrib.admin import TabularInline as BaseTabularInline
from django.contrib.admin import display, helpers
from django.contrib.admin.utils import lookup_field
from django.contrib.postgres.fields import ArrayField, IntegerRangeField
from django.contrib.postgres.search import SearchVectorField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import (
    BLANK_CHOICE_DASH,
    ForeignObjectRel,
    ManyToManyRel,
    OneToOneField,
)
from django.forms.utils import flatatt
from django.forms.widgets import SelectMultiple
from django.http import HttpRequest
from django.shortcuts import redirect
from django.template.defaultfilters import linebreaksbr
from django.template.loader import render_to_string
from django.urls import path, reverse
from django.utils.html import conditional_escape, format_html
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from unfold.utils import display_for_field

from .exceptions import UnfoldException
from .forms import ActionForm
from .settings import get_config
from .widgets import (
    CHECKBOX_LABEL_CLASSES,
    INPUT_CLASSES,
    LABEL_CLASSES,
    SELECT_CLASSES,
    UnfoldAdminBigIntegerFieldWidget,
    UnfoldAdminDecimalFieldWidget,
    UnfoldAdminEmailInputWidget,
    UnfoldAdminImageFieldWidget,
    UnfoldAdminImageSmallFieldWidget,
    UnfoldAdminIntegerFieldWidget,
    UnfoldAdminIntegerRangeWidget,
    UnfoldAdminNullBooleanSelectWidget,
    UnfoldAdminSingleDateWidget,
    UnfoldAdminSingleTimeWidget,
    UnfoldAdminSplitDateTimeWidget,
    UnfoldAdminTextareaWidget,
    UnfoldAdminTextInputWidget,
    UnfoldAdminUUIDInputWidget,
)

checkbox = forms.CheckboxInput({"class": "action-select"}, lambda value: False)

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
    models.UUIDField: {"widget": UnfoldAdminUUIDInputWidget},
    models.TextField: {"widget": UnfoldAdminTextareaWidget},
    models.NullBooleanField: {"widget": UnfoldAdminNullBooleanSelectWidget},
    models.IntegerField: {"widget": UnfoldAdminIntegerFieldWidget},
    models.BigIntegerField: {"widget": UnfoldAdminBigIntegerFieldWidget},
    models.DecimalField: {"widget": UnfoldAdminDecimalFieldWidget},
    models.FloatField: {"widget": UnfoldAdminDecimalFieldWidget},
    models.ImageField: {"widget": UnfoldAdminImageFieldWidget},
    models.JSONField: {"widget": UnfoldAdminTextareaWidget},
    ArrayField: {"widget": UnfoldAdminTextareaWidget},
    SearchVectorField: {"widget": UnfoldAdminTextareaWidget},
    IntegerRangeField: {"widget": UnfoldAdminIntegerRangeWidget},
}

FORMFIELD_OVERRIDES_INLINE = copy.deepcopy(FORMFIELD_OVERRIDES)

FORMFIELD_OVERRIDES_INLINE.update(
    {
        models.ImageField: {"widget": UnfoldAdminImageSmallFieldWidget},
    }
)


class UnfoldAdminField(helpers.AdminField):
    def label_tag(self):
        classes = []

        for lang, flag in get_config()["EXTENSIONS"]["modeltranslation"][
            "flags"
        ].items():
            if f"[{lang}]" in self.field.label:
                self.field.label = self.field.label.replace(f"[{lang}]", flag)
                break

        contents = conditional_escape(self.field.label)

        if self.is_checkbox:
            classes.append(" ".join(CHECKBOX_LABEL_CLASSES))
        else:
            classes.append(" ".join(LABEL_CLASSES))

        if self.field.field.required:
            classes.append("required")

        if not self.is_first:
            classes.append("inline")

        attrs = {"class": " ".join(classes)} if classes else {}
        required = mark_safe(' <span class="text-red-600">*</span>')

        return self.field.label_tag(
            contents=mark_safe(contents),
            attrs=attrs,
            label_suffix=required if self.field.field.required else "",
        )


helpers.AdminField = UnfoldAdminField


class UnfoldAdminReadonlyField(helpers.AdminReadonlyField):
    def label_tag(self):
        attrs = {
            "class": " ".join(LABEL_CLASSES + ["mb-2"]),
        }

        if not self.is_first:
            attrs["class"] = "inline"

        label = self.field["label"]

        return format_html(
            "<label{}>{}{}</label>",
            flatatt(attrs),
            capfirst(label),
            self.form.label_suffix,
        )

    def contents(self):
        contents = self._get_contents()

        self._preprocess_field(contents)

        return contents

    def _get_contents(self):
        from django.contrib.admin.templatetags.admin_list import _boolean_icon

        field, obj, model_admin = (
            self.field["field"],
            self.form.instance,
            self.model_admin,
        )
        try:
            f, attr, value = lookup_field(field, obj, model_admin)
        except (AttributeError, ValueError, ObjectDoesNotExist):
            result_repr = self.empty_value_display
        else:
            if field in self.form.fields:
                widget = self.form[field].field.widget
                # This isn't elegant but suffices for contrib.auth's
                # ReadOnlyPasswordHashWidget.
                if getattr(widget, "read_only", False):
                    return widget.render(field, value)
            if f is None:
                if getattr(attr, "boolean", False):
                    result_repr = _boolean_icon(value)
                else:
                    if hasattr(value, "__html__"):
                        result_repr = value
                    else:
                        result_repr = linebreaksbr(value)
            else:
                if isinstance(f.remote_field, ManyToManyRel) and value is not None:
                    result_repr = ", ".join(map(str, value.all()))
                elif (
                    isinstance(f.remote_field, (ForeignObjectRel, OneToOneField))
                    and value is not None
                ):
                    result_repr = self.get_admin_url(f.remote_field, value)
                else:
                    result_repr = display_for_field(value, f, self.empty_value_display)
                    return conditional_escape(result_repr)
                result_repr = linebreaksbr(result_repr)
        return conditional_escape(result_repr)

    def _preprocess_field(self, contents):
        if self.field["field"] in self.model_admin.readonly_preprocess_fields:
            func = self.model_admin.readonly_preprocess_fields[self.field["field"]]

            if isinstance(func, str):
                contents = import_string(func)(contents)
            elif callable(func):
                contents = func(contents)

        return contents


helpers.AdminReadonlyField = UnfoldAdminReadonlyField


class ModelAdminMixin:
    def __init__(self, model, admin_site):
        overrides = copy.deepcopy(FORMFIELD_OVERRIDES)

        for k, v in self.formfield_overrides.items():
            overrides.setdefault(k, {}).update(v)

        self.formfield_overrides = overrides

        super().__init__(model, admin_site)

    def formfield_for_choice_field(self, db_field, request: HttpRequest, **kwargs):
        # Overrides widget for CharFields which have choices attribute
        if "widget" not in kwargs:
            kwargs["widget"] = forms.Select(attrs={"class": " ".join(SELECT_CLASSES)})
            kwargs["choices"] = db_field.get_choices(
                include_blank=db_field.blank, blank_choice=[("", _("Select value"))]
            )

        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Overrides widgets for all related fields
        if "widget" not in kwargs:
            if db_field.name in self.raw_id_fields:
                kwargs["widget"] = forms.TextInput(
                    attrs={"class": " ".join(INPUT_CLASSES)}
                )
            elif (
                db_field.name not in self.get_autocomplete_fields(request)
                and db_field.name not in self.radio_fields
            ):
                kwargs["widget"] = forms.Select(
                    attrs={"class": " ".join(SELECT_CLASSES)}
                )
                kwargs["empty_label"] = _("Select value")

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if "widget" not in kwargs:
            if db_field.name in self.raw_id_fields:
                kwargs["widget"] = forms.TextInput(
                    attrs={"class": " ".join(INPUT_CLASSES)}
                )

        form_field = super().formfield_for_manytomany(db_field, request, **kwargs)

        # If M2M uses intermediary model, form_field will be None
        if not form_field:
            return None

        if isinstance(form_field.widget, SelectMultiple):
            form_field.widget.attrs["class"] = " ".join(SELECT_CLASSES)

        return form_field

    def formfield_for_nullboolean_field(self, db_field, request, **kwargs):
        if "widget" not in kwargs:
            kwargs["widget"] = forms.NullBooleanSelect(
                attrs={"class": " ".join(SELECT_CLASSES)}
            )

        return db_field.formfield(**kwargs)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, models.BooleanField) and db_field.null is True:
            return self.formfield_for_nullboolean_field(db_field, request, **kwargs)

        return super().formfield_for_dbfield(db_field, request, **kwargs)


class ModelAdmin(ModelAdminMixin, BaseModelAdmin):
    action_form = ActionForm
    actions_list = ()
    actions_row = ()
    actions_detail = ()
    actions_submit_line = ()
    custom_urls = ()
    add_fieldsets = ()
    list_filter_submit = False
    readonly_preprocess_fields = {}

    @property
    def media(self):
        media = super().media
        additional_media = forms.Media()

        for filter in self.list_filter:
            if not isinstance(filter, (tuple, list)):
                continue

            if hasattr(filter[1], "form_class") and hasattr(
                filter[1].form_class, "Media"
            ):
                additional_media += forms.Media(filter[1].form_class.Media)

        return media + additional_media

    def get_fieldsets(self, request, obj=None):
        if not obj and self.add_fieldsets:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_actions_list(self):
        return [self.get_unfold_action(action) for action in self.actions_list or []]

    def get_actions_detail(self):
        return [self.get_unfold_action(action) for action in self.actions_detail or []]

    def get_actions_row(self):
        return [self.get_unfold_action(action) for action in self.actions_row or []]

    def get_actions_submit_line(self):
        return [
            self.get_unfold_action(action) for action in self.actions_submit_line or []
        ]

    def get_custom_urls(self):
        """
        Method to get custom views for ModelAdmin with their urls

        Format of custom_urls item:
            ("path_to_view", "name_of_view", view_itself)
        """
        return () if self.custom_urls is None else self.custom_urls

    def get_urls(self):
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
                action["path"],
                wrap(action["method"]),
                name=action["action_name"],
            )
            for action in self.get_actions_list()
        ]

        action_detail_urls = [
            path(
                f"<path:object_id>/{action['path']}/",
                wrap(action["method"]),
                name=action["action_name"],
            )
            for action in self.get_actions_detail()
        ]

        action_row_urls = [
            path(
                f"<path:object_id>/{action['path']}",
                wrap(action["method"]),
                name=action["action_name"],
            )
            for action in self.get_actions_row()
        ]

        return (
            custom_urls
            + action_row_urls
            + actions_list_urls
            + action_detail_urls
            + urls
        )

    def _path_from_custom_url(self, custom_url):
        # TODO: wrap()
        return path(
            custom_url[0],
            self.admin_site.admin_view(custom_url[2]),
            {"model_admin": self},
            name=custom_url[1],
        )

    @display(description="")
    def actions_holder(self, instance):
        actions = [
            {
                "title": action["description"],
                "attrs": action["method"].attrs,
                "path": reverse(f"admin:{action['action_name']}", args=(instance.pk,)),
            }
            for action in self.get_actions_row()
        ]
        return render_to_string(
            "unfold/helpers/actions_row.html",
            context={
                "instance": instance,
                "actions": actions,
            },
        )

    def get_list_display(self, request):
        if len(self.get_actions_row()) > 0:
            return super().get_list_display(request) + ("actions_holder",)
        return super().get_list_display(request)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if extra_context is None:
            extra_context = {}

        actions = []
        if object_id:
            for action in self.get_actions_detail():
                actions.append(
                    {
                        "title": action["description"],
                        "attrs": action["method"].attrs,
                        "path": reverse(
                            f"admin:{action['action_name']}", args=(object_id,)
                        ),
                    }
                )

        extra_context.update(
            {
                "actions_submit_line": self.get_actions_submit_line(),
                "actions_detail": actions,
            }
        )

        return super().changeform_view(request, object_id, form_url, extra_context)

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        actions = [
            {
                "title": action["description"],
                "attrs": action["method"].attrs,
                "path": reverse(f"admin:{action['action_name']}"),
            }
            for action in self.get_actions_list()
        ]

        extra_context.update({"actions_list": actions})

        return super().changelist_view(request, extra_context)

    def get_unfold_action(self, action):
        method = self._get_instance_method(action)

        return {
            "action_name": f"{self.model._meta.app_label}_{self.model._meta.model_name}_{action}",
            "method": method,
            "description": self._get_action_description(method, action),
            "path": self._get_action_url(method, action),
        }

    @staticmethod
    def _get_action_url(func, name):
        return getattr(func, "url_path", name)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        for action_attrs in self.get_actions_submit_line():
            if action_attrs["action_name"] not in request.POST:
                continue

            action_attrs["method"](request, obj)

    def _get_instance_method(self, method_name):
        try:
            method = getattr(self, method_name)
        except AttributeError as e:
            raise UnfoldException(
                f"Method {method_name} specified does not exist on current object"
            ) from e

        if not callable(method):
            raise UnfoldException(f"{method_name} is not callable")

        return method

    def get_action_choices(self, request, default_choices=BLANK_CHOICE_DASH):
        default_choices = [("", _("Select action"))]
        return super().get_action_choices(request, default_choices)

    @display(description=mark_safe('<input type="checkbox" id="action-toggle">'))
    def action_checkbox(self, obj):
        return checkbox.render(helpers.ACTION_CHECKBOX_NAME, str(obj.pk))

    def response_change(self, request, obj):
        res = super().response_change(request, obj)
        if "next" in request.GET:
            return redirect(request.GET["next"])
        return res

    def response_add(self, request, obj, post_url_continue=None):
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
