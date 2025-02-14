from django.contrib.admin import helpers
from django.contrib.admin.utils import lookup_field, quote
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import (
    ForeignObjectRel,
    ImageField,
    JSONField,
    ManyToManyRel,
    OneToOneField,
)
from django.forms.utils import flatatt
from django.template.defaultfilters import linebreaksbr
from django.urls import NoReverseMatch, reverse
from django.utils.html import conditional_escape, format_html
from django.utils.module_loading import import_string
from django.utils.safestring import SafeText, mark_safe
from django.utils.text import capfirst

from unfold.mixins import BaseModelAdminMixin
from unfold.settings import get_config
from unfold.utils import display_for_field, prettify_json
from unfold.widgets import CHECKBOX_LABEL_CLASSES, LABEL_CLASSES


class UnfoldAdminReadonlyField(helpers.AdminReadonlyField):
    def label_tag(self) -> SafeText:
        from .admin import ModelAdmin

        if not isinstance(self.model_admin, ModelAdmin) and not isinstance(
            self.model_admin, BaseModelAdminMixin
        ):
            return super().label_tag()

        attrs = {
            "class": " ".join(LABEL_CLASSES + ["mb-2"]),
        }

        label = self.field["label"]

        return format_html(
            "<label{}>{}{}</label>",
            flatatt(attrs),
            capfirst(label),
            self.form.label_suffix,
        )

    def is_json(self) -> bool:
        field, obj, model_admin = (
            self.field["field"],
            self.form.instance,
            self.model_admin,
        )

        try:
            f, attr, value = lookup_field(field, obj, model_admin)
        except (AttributeError, ValueError, ObjectDoesNotExist):
            return False

        return isinstance(f, JSONField)

    def is_image(self) -> bool:
        field, obj, model_admin = (
            self.field["field"],
            self.form.instance,
            self.model_admin,
        )

        try:
            f, attr, value = lookup_field(field, obj, model_admin)
        except (AttributeError, ValueError, ObjectDoesNotExist):
            return False

        if hasattr(attr, "image"):
            return attr.image
        elif (
            isinstance(attr, property)
            and hasattr(attr, "fget")
            and hasattr(attr.fget, "image")
        ):
            return attr.fget.image

        return isinstance(f, ImageField)

    def contents(self) -> str:
        contents = self._get_contents()
        contents = self._preprocess_field(contents)
        return contents

    def get_admin_url(self, remote_field, remote_obj):
        url_name = f"admin:{remote_field.model._meta.app_label}_{remote_field.model._meta.model_name}_change"
        try:
            url = reverse(
                url_name,
                args=[quote(remote_obj.pk)],
                current_app=self.model_admin.admin_site.name,
            )
            return format_html(
                '<a href="{}" class="text-primary-600 dark:text-primary-500">{}</a>',
                url,
                remote_obj,
            )
        except NoReverseMatch:
            return str(remote_obj)

    def _get_contents(self) -> str:
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
                elif isinstance(f, models.JSONField):
                    formatted_output = prettify_json(value)

                    if formatted_output:
                        return formatted_output

                    result_repr = display_for_field(value, f, self.empty_value_display)
                    return conditional_escape(result_repr)
                elif isinstance(f, models.URLField):
                    return format_html(
                        '<a href="{}" class="text-primary-600 dark:text-primary-500">{}</a>',
                        value,
                        value,
                    )
                else:
                    result_repr = display_for_field(value, f, self.empty_value_display)
                    return conditional_escape(result_repr)
                result_repr = linebreaksbr(result_repr)
        return conditional_escape(result_repr)

    def _preprocess_field(self, contents: str) -> str:
        if (
            hasattr(self.model_admin, "readonly_preprocess_fields")
            and self.field["field"] in self.model_admin.readonly_preprocess_fields
        ):
            func = self.model_admin.readonly_preprocess_fields[self.field["field"]]
            if isinstance(func, str):
                contents = import_string(func)(contents)
            elif callable(func):
                contents = func(contents)

        return contents


class UnfoldAdminField(helpers.AdminField):
    def label_tag(self) -> SafeText:
        classes = []
        if not self.field.field.widget.__class__.__name__.startswith(
            "Unfold"
        ) and not self.field.field.widget.template_name.startswith("unfold"):
            return super().label_tag()

        # TODO load config from current AdminSite (override Fieldline.__iter__ method)
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

        attrs = {"class": " ".join(classes)} if classes else {}
        required = mark_safe(' <span class="text-red-600">*</span>')

        return self.field.label_tag(
            contents=mark_safe(contents),
            attrs=attrs,
            label_suffix=required if self.field.field.required else "",
        )
