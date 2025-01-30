from collections.abc import Generator
from typing import Any, Optional

from django.contrib.admin.views.main import ChangeList
from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet
from django.forms import ValidationError
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from unfold.contrib.filters.forms import (
    AutocompleteDropdownForm,
    DropdownForm,
    RangeNumericForm,
)


class ValueMixin:
    def value(self) -> Optional[str]:
        return (
            self.lookup_val[0]
            if self.lookup_val not in EMPTY_VALUES
            and isinstance(self.lookup_val, list)
            and len(self.lookup_val) > 0
            else self.lookup_val
        )


class MultiValueMixin:
    def value(self) -> Optional[list[str]]:
        return (
            self.lookup_val
            if self.lookup_val not in EMPTY_VALUES
            and isinstance(self.lookup_val, list)
            and len(self.lookup_val) > 0
            else self.lookup_val
        )


class DropdownMixin:
    template = "unfold/filters/filters_field.html"
    form_class = DropdownForm
    all_option = ["", _("All")]

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.value() not in EMPTY_VALUES:
            return super().queryset(request, queryset)

        return queryset


class RangeNumericMixin:
    request = None
    parameter_name = None
    template = "unfold/filters/filters_numeric_range.html"

    def init_used_parameters(self, params: dict[str, Any]) -> None:
        if self.parameter_name + "_from" in params:
            value = params.pop(self.parameter_name + "_from")

            self.used_parameters[self.parameter_name + "_from"] = (
                value[0] if isinstance(value, list) else value
            )

        if self.parameter_name + "_to" in params:
            value = params.pop(self.parameter_name + "_to")
            self.used_parameters[self.parameter_name + "_to"] = (
                value[0] if isinstance(value, list) else value
            )

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        filters = {}

        value_from = self.used_parameters.get(self.parameter_name + "_from", None)
        if value_from is not None and value_from != "":
            filters.update(
                {
                    self.parameter_name + "__gte": self.used_parameters.get(
                        self.parameter_name + "_from", None
                    ),
                }
            )

        value_to = self.used_parameters.get(self.parameter_name + "_to", None)
        if value_to is not None and value_to != "":
            filters.update(
                {
                    self.parameter_name + "__lte": self.used_parameters.get(
                        self.parameter_name + "_to", None
                    ),
                }
            )

        try:
            return queryset.filter(**filters)
        except (ValueError, ValidationError):
            return None

    def expected_parameters(self) -> list[str]:
        return [
            f"{self.parameter_name}_from",
            f"{self.parameter_name}_to",
        ]

    def choices(self, changelist: ChangeList) -> tuple[dict[str, Any], ...]:
        return (
            {
                "request": self.request,
                "parameter_name": self.parameter_name,
                "form": RangeNumericForm(
                    name=self.parameter_name,
                    data={
                        self.parameter_name + "_from": self.used_parameters.get(
                            self.parameter_name + "_from", None
                        ),
                        self.parameter_name + "_to": self.used_parameters.get(
                            self.parameter_name + "_to", None
                        ),
                    },
                ),
            },
        )


class AutocompleteMixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if "request" in kwargs:
            self.request = kwargs["request"]

    def choices(
        self, changelist: ChangeList
    ) -> Generator[dict[str, AutocompleteDropdownForm], None, None]:
        yield {
            "form": self.form_class(
                request=self.request,
                label=_("By %(filter_title)s") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=(),
                field=self.field,
                model_admin=self.model_admin,
                data={self.lookup_kwarg: self.value()},
                multiple=self.multiple if hasattr(self, "multiple") else False,
            ),
        }
