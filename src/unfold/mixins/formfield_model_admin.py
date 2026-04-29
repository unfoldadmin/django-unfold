import copy
from typing import Any

from django.conf import settings
from django.contrib.admin.options import BaseModelAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.widgets import (
    FilteredSelectMultiple,
    RelatedFieldWidgetWrapper,
)
from django.db import models
from django.db.models.fields import Field
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.forms.fields import Field as FormField
from django.forms.fields import TypedChoiceField
from django.forms.models import ModelChoiceField, ModelMultipleChoiceField
from django.forms.widgets import SelectMultiple
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from unfold import widgets
from unfold.overrides import FORMFIELD_OVERRIDES
from unfold.utils import get_setting_value


class FormFieldModelAdminMixin(BaseModelAdmin):
    # List of all db fields which are not available in autocomplete_fields
    _autocomplete_fields_missing: list[str] = []
    autocomplete_fields_excluded_from_warnings: list[str] = []

    def __init__(self, model: type[models.Model], admin_site: AdminSite) -> None:
        overrides = copy.deepcopy(FORMFIELD_OVERRIDES)

        for k, v in self.formfield_overrides.items():
            overrides.setdefault(k, {}).update(v)

        self.formfield_overrides = overrides

        super().__init__(model, admin_site)

    def formfield_for_choice_field(
        self, db_field: Field, request: HttpRequest, **kwargs: Any
    ) -> TypedChoiceField | None:
        if "widget" not in kwargs:
            if db_field.name in self.radio_fields:
                kwargs["widget"] = widgets.UnfoldAdminRadioSelectWidget(
                    radio_style=self.radio_fields[db_field.name]
                )
            else:
                kwargs["widget"] = widgets.UnfoldAdminSelectWidget()

        if "choices" not in kwargs:
            kwargs["choices"] = db_field.get_choices(
                include_blank=db_field.blank, blank_choice=[("", _("Select value"))]
            )

        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def formfield_for_foreignkey(
        self, db_field: ForeignKey, request: HttpRequest, **kwargs: Any
    ) -> ModelChoiceField | None:
        # Overrides widgets for all related fields
        if "widget" not in kwargs:
            if db_field.name in self.raw_id_fields:
                kwargs["widget"] = widgets.UnfoldForeignKeyRawIdWidget(
                    db_field.remote_field, self.admin_site, using=kwargs.get("using")
                )
            elif (
                db_field.name not in self.get_autocomplete_fields(request)
                and db_field.name not in self.radio_fields
            ):
                kwargs["widget"] = widgets.UnfoldAdminSelectWidget()
                kwargs["empty_label"] = _("Select value")

        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        self._check_autocomplete_field(db_field, formfield, request)
        return formfield

    def formfield_for_manytomany(
        self,
        db_field: ManyToManyField,
        request: HttpRequest,
        **kwargs: Any,
    ) -> ModelMultipleChoiceField | None:
        formfield = super().formfield_for_manytomany(db_field, request, **kwargs)

        # If M2M uses intermediary model, form_field will be None
        if not formfield:
            return None

        if isinstance(formfield.widget, SelectMultiple):
            formfield.widget.attrs["class"] = " ".join(widgets.SELECT_CLASSES)

        self._check_autocomplete_field(db_field, formfield, request)
        return formfield

    def formfield_for_nullboolean_field(
        self, db_field: Field, request: HttpRequest, **kwargs: Any
    ) -> FormField | None:
        if "widget" not in kwargs:
            if db_field.choices:
                kwargs["widget"] = widgets.UnfoldAdminSelectWidget(
                    choices=list(db_field.choices)
                )
            else:
                kwargs["widget"] = widgets.UnfoldAdminNullBooleanSelectWidget()

        return db_field.formfield(**kwargs)

    def formfield_for_dbfield(
        self, db_field: Field, request: HttpRequest, **kwargs: Any
    ) -> FormField | None:
        if isinstance(db_field, models.BooleanField) and db_field.null is True:
            return self.formfield_for_nullboolean_field(db_field, request, **kwargs)

        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)

        if formfield and isinstance(formfield.widget, RelatedFieldWidgetWrapper):
            formfield.widget.template_name = (
                "unfold/widgets/related_widget_wrapper.html"
            )

        return formfield

    def _check_autocomplete_field(  # noqa: PLR0911
        self,
        db_field: Field,
        formfield: ModelChoiceField | ModelMultipleChoiceField | None,
        request: HttpRequest,
    ) -> None:
        # Run only in debug mode
        if not settings.DEBUG:
            return

        # Show warnings only if enabled in UNFOLD settings
        if get_setting_value("SHOW_UI_WARNINGS", request) is False:
            return

        # Field is already in autocomplete_fields
        if db_field.name in self.get_autocomplete_fields(request):
            return

        # Readonly fields are not rendering large select dropdown
        if db_field.name in self.get_readonly_fields(request):
            return

        # Raw ID field, no problem with SQL queries
        if db_field.name in self.raw_id_fields:
            return

        # Make an exception for this special widget
        if formfield is not None and isinstance(
            formfield.widget, FilteredSelectMultiple
        ):
            return

        # Sometimes we want to exclude a field from the warnings
        if db_field.name in self.autocomplete_fields_excluded_from_warnings:
            return

        self._autocomplete_fields_missing.append(db_field.name)
