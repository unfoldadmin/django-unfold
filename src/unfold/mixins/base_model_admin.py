import copy
from typing import Optional

from django.contrib.admin.sites import AdminSite
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.db import models
from django.db.models.fields import Field
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.forms.fields import TypedChoiceField
from django.forms.models import ModelChoiceField, ModelMultipleChoiceField
from django.forms.widgets import SelectMultiple
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from unfold.overrides import FORMFIELD_OVERRIDES
from unfold.widgets import (
    SELECT_CLASSES,
    UnfoldAdminNullBooleanSelectWidget,
    UnfoldAdminRadioSelectWidget,
    UnfoldAdminSelectWidget,
    UnfoldAdminTextInputWidget,
    UnfoldForeignKeyRawIdWidget,
)


class BaseModelAdminMixin:
    def __init__(self, model: models.Model, admin_site: AdminSite) -> None:
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
