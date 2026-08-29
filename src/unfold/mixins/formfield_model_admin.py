import copy
from collections.abc import Mapping
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.options import BaseModelAdmin, InlineModelAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.widgets import (
    FilteredSelectMultiple,
    RelatedFieldWidgetWrapper,
)
from django.core import checks
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models.fields import Field
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.forms.fields import Field as FormField
from django.forms.fields import TypedChoiceField
from django.forms.models import ModelChoiceField, ModelMultipleChoiceField
from django.forms.widgets import SelectMultiple
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from unfold import widgets
from unfold.overrides import FORMFIELD_OVERRIDES
from unfold.utils import get_setting_value


class FormFieldModelAdminMixin(BaseModelAdmin):
    # List of all db fields which are not available in autocomplete_fields
    _autocomplete_fields_missing: list[str] = []
    autocomplete_fields_excluded_from_warnings: list[str] = []
    autocomplete_dependencies: dict[str, str | dict[str, str]] = {}

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

    def get_autocomplete_dependency_config(
        self, field_name: str
    ) -> dict[str, str] | None:
        dependencies = self.autocomplete_dependencies
        if not isinstance(dependencies, Mapping):
            return None
        dependency = dependencies.get(field_name)
        if isinstance(dependency, str):
            return {"depends_on": dependency, "lookup": dependency}
        if not isinstance(dependency, Mapping):
            return None
        depends_on = dependency.get("depends_on")
        lookup = dependency.get("lookup")
        if not isinstance(depends_on, str) or not isinstance(lookup, str):
            return None
        return {"depends_on": depends_on, "lookup": lookup}

    def get_dependent_autocomplete_url_name(self) -> str:
        if isinstance(self, InlineModelAdmin):
            parent = self.parent_model._meta
            inline_name = self.__class__.__name__.lower()
            return (
                f"{parent.app_label}_{parent.model_name}_{inline_name}"
                "_dependent_autocomplete"
            )

        opts = self.model._meta
        return f"{opts.app_label}_{opts.model_name}_dependent_autocomplete"

    def formfield_for_foreignkey(
        self, db_field: ForeignKey, request: HttpRequest, **kwargs: Any
    ) -> ModelChoiceField | None:
        # Overrides widgets for all related fields
        if "widget" not in kwargs:
            if db_field.name in self.raw_id_fields:
                kwargs["widget"] = widgets.UnfoldForeignKeyRawIdWidget(
                    db_field.remote_field, self.admin_site, using=kwargs.get("using")
                )
            elif db_field.name in self.get_autocomplete_fields(request):
                dependency = self.get_autocomplete_dependency_config(db_field.name)
                if dependency:
                    kwargs["widget"] = widgets.UnfoldAdminDependentAutocompleteSelect(
                        db_field,
                        self.admin_site,
                        using=kwargs.get("using"),
                        parent_field_name=dependency["depends_on"],
                        source_admin=self,
                    )
            elif db_field.name not in self.radio_fields:
                kwargs["widget"] = widgets.UnfoldAdminSelectWidget()
                kwargs["empty_label"] = _("Select value")

        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)

        if self._show_ui_warnings(request):
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

        if self._show_ui_warnings(request):
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

    def _show_ui_warnings(self, request: HttpRequest) -> bool:
        return (
            request.method == "GET"
            and settings.DEBUG
            and get_setting_value("SHOW_UI_WARNINGS", request) is True
        )

    def _display_autocomplete_fields_warnings(self, request: HttpRequest) -> None:
        for missing_field in sorted(self._autocomplete_fields_missing):
            messages.warning(
                request,
                format_html(
                    _(
                        'Field <strong class="font-semibold">{field_name}</strong> is not an autocomplete field. Please add it to the `autocomplete_fields` list.'
                    ),  # ty:ignore[invalid-argument-type]
                    field_name=missing_field,
                ),
            )

            if missing_field in self._autocomplete_fields_missing:
                self._autocomplete_fields_missing.remove(missing_field)

    def _check_autocomplete_field(  # noqa: PLR0911
        self,
        db_field: Field,
        formfield: ModelChoiceField | ModelMultipleChoiceField | None,
        request: HttpRequest,
    ) -> None:
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

        field_name = f"{self.__class__.__name__}.{db_field.name}"

        if field_name not in self._autocomplete_fields_missing:
            self._autocomplete_fields_missing.append(field_name)

    def _check_autocomplete_dependencies(self) -> list[checks.Error]:
        dependencies = self.autocomplete_dependencies
        if not dependencies:
            return []
        if not isinstance(dependencies, Mapping):
            return [
                checks.Error(
                    "autocomplete_dependencies must be a mapping of child field to parent field.",
                    obj=self,
                    id="unfold.E001",
                )
            ]

        errors = []
        autocomplete_fields = set(self.autocomplete_fields)
        for child_name, dependency in dependencies.items():
            if not isinstance(child_name, str):
                errors.append(
                    checks.Error(
                        "autocomplete_dependencies keys must be field names.",
                        obj=self,
                        id="unfold.E002",
                    )
                )
                continue
            if isinstance(dependency, str):
                parent_name = dependency
                lookup = dependency
            elif isinstance(dependency, Mapping):
                parent_name = dependency.get("depends_on")
                lookup = dependency.get("lookup")
            else:
                parent_name = lookup = None
            if not isinstance(parent_name, str) or not isinstance(lookup, str):
                errors.append(
                    checks.Error(
                        "Each dependency must be a parent field name or a mapping with "
                        "'depends_on' and 'lookup' field names.",
                        obj=self,
                        id="unfold.E002",
                    )
                )
                continue
            if "__" in lookup:
                errors.append(
                    checks.Error(
                        "Dependency lookup must be a single ForeignKey field name, not a relation lookup.",
                        obj=self,
                        id="unfold.E008",
                    )
                )
                continue
            if child_name not in autocomplete_fields:
                errors.append(
                    checks.Error(
                        f"'{child_name}' must also be listed in autocomplete_fields.",
                        obj=self,
                        id="unfold.E003",
                    )
                )
                continue
            errors.extend(
                self._check_autocomplete_dependency_fields(
                    child_name, parent_name, lookup
                )
            )
        return errors

    def _check_autocomplete_dependency_fields(
        self, child_name: str, parent_name: str, lookup: str
    ) -> list[checks.Error]:
        try:
            child_field = self.model._meta.get_field(child_name)
            parent_field = self.model._meta.get_field(parent_name)
        except FieldDoesNotExist:
            return [
                checks.Error(
                    f"'{child_name}' and '{parent_name}' must be fields on {self.model._meta.label}.",
                    obj=self,
                    id="unfold.E004",
                )
            ]
        if not isinstance(child_field, models.ForeignKey) or not isinstance(
            parent_field, models.ForeignKey
        ):
            return [
                checks.Error(
                    "Dependent autocompletes require ForeignKey child and parent fields.",
                    obj=self,
                    id="unfold.E005",
                )
            ]
        try:
            target_parent_field = child_field.remote_field.model._meta.get_field(lookup)
        except FieldDoesNotExist:
            return [
                checks.Error(
                    f"{child_field.remote_field.model._meta.label} needs a ForeignKey named '{lookup}'.",
                    obj=self,
                    id="unfold.E006",
                )
            ]
        if not isinstance(target_parent_field, models.ForeignKey) or (
            target_parent_field.remote_field.model
            is not parent_field.remote_field.model
        ):
            return [
                checks.Error(
                    f"'{lookup}' on {child_field.remote_field.model._meta.label} must point to "
                    f"{parent_field.remote_field.model._meta.label}.",
                    obj=self,
                    id="unfold.E007",
                )
            ]
        return []
