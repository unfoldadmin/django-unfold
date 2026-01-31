from typing import TYPE_CHECKING, Any

from django.contrib.admin import helpers
from django.contrib.admin.utils import lookup_field, quote
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import (
    Field,
    FileField,
    ForeignObjectRel,
    ImageField,
    JSONField,
    ManyToManyRel,
    OneToOneField,
)
from django.forms import ModelChoiceField, ModelMultipleChoiceField, Widget
from django.forms.utils import flatatt
from django.template.defaultfilters import linebreaksbr
from django.urls import NoReverseMatch, reverse, reverse_lazy
from django.utils.html import conditional_escape, format_html
from django.utils.module_loading import import_string
from django.utils.safestring import SafeString, SafeText, mark_safe
from django.utils.text import capfirst

from unfold.settings import get_config
from unfold.utils import display_for_field, prettify_json
from unfold.widgets import (
    CHECKBOX_LABEL_CLASSES,
    LABEL_CLASSES,
    UnfoldAdminAutocompleteModelChoiceFieldWidget,
    UnfoldAdminMultipleAutocompleteModelChoiceFieldWidget,
)

if TYPE_CHECKING:
    from unfold.admin import ModelAdmin


class UnfoldAdminReadonlyField(helpers.AdminReadonlyField):
    model_admin: "ModelAdmin"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.resolved_field = self._resolve_field()

    def label_tag(self) -> SafeText:
        attrs = {
            "class": " ".join(LABEL_CLASSES + ["mb-2"]),
        }

        label = self.field["label"]

        return format_html("<label{}>{}</label>", flatatt(attrs), capfirst(label))

    @property
    def url(self) -> str | bool:
        if not self.is_file:
            return False

        field_name = self.field["field"]
        if isinstance(field_name, str) and hasattr(self.form.instance, field_name):
            field_value = getattr(self.form.instance, field_name)

            if field_value and hasattr(field_value, "url"):
                return field_value.url

        return False

    @property
    def is_json(self) -> bool:
        if isinstance(self.resolved_field, bool) or not self.resolved_field:
            return False

        f, attr, value = self.resolved_field

        return isinstance(f, JSONField)

    @property
    def is_image(self) -> bool:
        if isinstance(self.resolved_field, bool) or not self.resolved_field:
            return False

        f, attr, value = self.resolved_field

        return isinstance(f, ImageField)

    @property
    def is_file(self) -> bool:
        if isinstance(self.resolved_field, bool) or not self.resolved_field:
            return False

        f, attr, value = self.resolved_field
        return isinstance(f, ImageField | FileField)

    def contents(self) -> SafeString:
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
            return format_html('<a href="{}" class="text-link">{}</a>', url, remote_obj)
        except NoReverseMatch:
            return str(remote_obj)

    def _get_contents(self) -> SafeString:  # noqa: PLR0912
        from unfold.utils import _boolean_icon

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
            if isinstance(field, str) and field in self.form.fields:
                widget = self.form[field].field.widget
                # This isn't elegant but suffices for contrib.auth's
                # ReadOnlyPasswordHashWidget.
                if getattr(widget, "read_only", False):
                    return widget.render(field, value)

            if f is None:
                if getattr(attr, "boolean", False):
                    result_repr = _boolean_icon(value)
                elif hasattr(value, "__html__"):
                    result_repr = value
                else:
                    result_repr = linebreaksbr(value)
            else:
                if isinstance(f.remote_field, ManyToManyRel) and value is not None:
                    result_repr = ", ".join(map(str, value.all()))
                elif (
                    isinstance(f.remote_field, ForeignObjectRel | OneToOneField)
                    and value is not None
                ):
                    result_repr = self.get_admin_url(f.remote_field, value)
                elif isinstance(f, models.JSONField):
                    formatted_output = prettify_json(value, f.encoder)

                    if formatted_output:
                        return formatted_output

                    result_repr = display_for_field(value, f, self.empty_value_display)
                    return conditional_escape(result_repr)
                elif isinstance(f, models.URLField):
                    return value and format_html(
                        '<a href="{}" class="text-link">{}</a>', value, value
                    )
                else:
                    result_repr = display_for_field(value, f, self.empty_value_display)
                    return conditional_escape(result_repr)
                result_repr = linebreaksbr(result_repr)
        return conditional_escape(result_repr)

    def _preprocess_field(self, contents: SafeString) -> SafeString:
        if (
            hasattr(self.model_admin, "readonly_preprocess_fields")
            and self.field["field"]
            in self.model_admin.readonly_preprocess_fields.keys()
        ):
            func = self.model_admin.readonly_preprocess_fields[self.field["field"]]
            if isinstance(func, str):
                contents = import_string(func)(contents)
            elif callable(func):
                contents = func(contents)

        return contents

    def _resolve_field(self) -> bool | tuple[Field | None, str | None, Any]:
        field, obj, model_admin = (
            self.field["field"],
            self.form.instance,
            self.model_admin,
        )

        try:
            return lookup_field(field, obj, model_admin)
        except (AttributeError, ValueError, ObjectDoesNotExist):
            pass

        return False


class UnfoldAdminField(helpers.AdminField):
    def label_tag(self) -> SafeText:
        classes = []

        # TODO load config from current AdminSite (override Fieldline.__iter__ method)
        flags = get_config()["EXTENSIONS"]["modeltranslation"]["flags"]

        for lang, flag in flags.items():
            if f"[{lang}]" in self.field.label:
                self.field.label = self.field.label.replace(f"[{lang}]", flag)
                break

        contents = conditional_escape(self.field.label)

        classes.append(
            " ".join(CHECKBOX_LABEL_CLASSES if self.is_checkbox else LABEL_CLASSES)
        )

        if self.field.field.required:
            classes.append("required")

        attrs = {"class": " ".join(classes)} if classes else {}
        required = mark_safe(' <span class="text-red-600">*</span>')

        return self.field.label_tag(
            contents=mark_safe(contents),
            attrs=attrs,
            label_suffix=required if self.field.field.required else "",
        )


class AutocompleteFieldMixin:
    def __init__(self, url_path: str, *args: Any, **kwargs: Any) -> None:
        self.url_path = url_path
        super().__init__(*args, **kwargs)

    def widget_attrs(self, widget: Widget) -> dict[str, Any]:
        return {
            "data-ajax--url": reverse_lazy(self.url_path),
        }


class UnfoldAdminAutocompleteModelChoiceField(AutocompleteFieldMixin, ModelChoiceField):
    widget = UnfoldAdminAutocompleteModelChoiceFieldWidget


class UnfoldAdminMultipleAutocompleteModelChoiceField(
    AutocompleteFieldMixin, ModelMultipleChoiceField
):
    widget = UnfoldAdminMultipleAutocompleteModelChoiceFieldWidget
