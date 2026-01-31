from collections.abc import Callable, Iterator
from typing import Any

from django.contrib.admin import (
    ChoicesFieldListFilter,
    ListFilter,
    RelatedFieldListFilter,
)
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.db.models import QuerySet
from django.db.models.fields import BLANK_CHOICE_DASH
from django.db.models.fields.related import RelatedField
from django.forms import ValidationError
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from unfold.contrib.filters.forms import (
    AutocompleteDropdownForm,
    CheckboxForm,
    DropdownForm,
    RadioForm,
    RangeNumericForm,
)


class ValueMixin:
    lookup_val = None

    def value(self) -> str | None:
        if isinstance(self.lookup_val, list) and len(self.lookup_val):
            return self.lookup_val[0]

        return self.lookup_val


class MultiValueMixin:
    lookup_val = None

    def value(self) -> list[str] | None:
        return self.lookup_val


class DropdownMixin:
    template = "unfold/filters/filters_field.html"
    form_class = DropdownForm
    all_option = ["", _("All")]


class ChoicesMixin(ChoicesFieldListFilter):
    template = "unfold/filters/filters_field.html"
    all_option: tuple[str, str] | None = None
    form_class: type[CheckboxForm | RadioForm]
    value: Callable

    def choices(self, changelist: ChangeList) -> Iterator:
        add_facets = getattr(changelist, "add_facets", False)
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None
        choices = [self.all_option] if self.all_option else []

        for i, choice in enumerate(self.field.flatchoices):
            if add_facets and facet_counts:
                count = facet_counts[f"{i}__c"]
                choices.append((choice[0], f"{choice[1]} ({count})"))
            else:
                choices.append(choice)

        yield {
            "form": self.form_class(
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=choices,
                data={
                    self.lookup_kwarg: self.value(),
                },
            ),
        }


class RangeNumericMixin(ListFilter):
    request = None
    template = "unfold/filters/filters_numeric_range.html"
    parameter_name: str | None = None

    def init_used_parameters(self, params: dict[str, Any]) -> None:
        if f"{self.parameter_name}_from" in params:
            value = params.pop(f"{self.parameter_name}_from")

            self.used_parameters[f"{self.parameter_name}_from"] = (
                value[0] if isinstance(value, list) else value
            )

        if f"{self.parameter_name}_to" in params:
            value = params.pop(f"{self.parameter_name}_to")
            self.used_parameters[f"{self.parameter_name}_to"] = (
                value[0] if isinstance(value, list) else value
            )

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet | None:
        filters = {}

        value_from = self.used_parameters.get(f"{self.parameter_name}_from", None)
        if value_from is not None and value_from != "":
            filters.update(
                {
                    f"{self.parameter_name}__gte": self.used_parameters.get(
                        f"{self.parameter_name}_from", None
                    ),
                }
            )

        value_to = self.used_parameters.get(f"{self.parameter_name}_to", None)
        if value_to is not None and value_to != "":
            filters.update(
                {
                    f"{self.parameter_name}__lte": self.used_parameters.get(
                        f"{self.parameter_name}_to", None
                    ),
                }
            )

        try:
            return queryset.filter(**filters)
        except (ValueError, ValidationError):
            return None

    def expected_parameters(self) -> list[str | None]:
        return [
            f"{self.parameter_name}_from",
            f"{self.parameter_name}_to",
        ]

    def choices(self, changelist: ChangeList) -> Iterator:
        if self.parameter_name:
            yield {
                "request": self.request,
                "parameter_name": self.parameter_name,
                "form": RangeNumericForm(
                    name=self.parameter_name,
                    data={
                        f"{self.parameter_name}_from": self.used_parameters.get(
                            f"{self.parameter_name}_from", None
                        ),
                        f"{self.parameter_name}_to": self.used_parameters.get(
                            f"{self.parameter_name}_to", None
                        ),
                    },
                ),
            }


class AutocompleteMixin(RelatedFieldListFilter):
    model_admin: ModelAdmin
    form_class: type[AutocompleteDropdownForm]
    value: Callable

    def has_output(self) -> bool:
        return True

    def field_choices(
        self, field: RelatedField, request: HttpRequest, model_admin: ModelAdmin
    ) -> list[tuple]:
        return [
            ("", BLANK_CHOICE_DASH),
        ]

    def choices(self, changelist: ChangeList) -> Iterator:
        yield {
            "form": self.form_class(
                request=self.request,
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=(),
                field=self.field,
                model_admin=self.model_admin,
                data={
                    self.lookup_kwarg: self.value(),
                },
                multiple=self.multiple
                if hasattr(self, "multiple") and isinstance(self.multiple, bool)
                else False,
            ),
        }
