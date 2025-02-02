from typing import Any

from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.core.validators import EMPTY_VALUES
from django.db.models import Model, QuerySet
from django.db.models.fields import (
    DateField,
    DateTimeField,
    Field,
)
from django.forms import ValidationError
from django.http import HttpRequest

from unfold.contrib.filters.forms import (
    RangeDateForm,
    RangeDateTimeForm,
)
from unfold.utils import parse_date_str, parse_datetime_str


class RangeDateFilter(admin.FieldListFilter):
    request = None
    parameter_name = None
    form_class = RangeDateForm
    template = "unfold/filters/filters_date_range.html"

    def __init__(
        self,
        field: Field,
        request: HttpRequest,
        params: dict[str, str],
        model: type[Model],
        model_admin: ModelAdmin,
        field_path: str,
    ) -> None:
        super().__init__(field, request, params, model, model_admin, field_path)
        if not isinstance(field, DateField):
            raise TypeError(
                f"Class {type(self.field)} is not supported for {self.__class__.__name__}."
            )

        self.request = request
        if self.parameter_name is None:
            self.parameter_name = self.field_path

        if self.parameter_name + "_from" in params:
            value = params.pop(self.field_path + "_from")
            value = value[0] if isinstance(value, list) else value

            if value not in EMPTY_VALUES:
                self.used_parameters[self.field_path + "_from"] = value

        if self.parameter_name + "_to" in params:
            value = params.pop(self.field_path + "_to")
            value = value[0] if isinstance(value, list) else value

            if value not in EMPTY_VALUES:
                self.used_parameters[self.field_path + "_to"] = value

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        filters = {}

        value_from = self.used_parameters.get(self.parameter_name + "_from")
        if value_from not in EMPTY_VALUES:
            filters.update({self.parameter_name + "__gte": parse_date_str(value_from)})

        value_to = self.used_parameters.get(self.parameter_name + "_to")
        if value_to not in EMPTY_VALUES:
            filters.update({self.parameter_name + "__lte": parse_date_str(value_to)})

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
                "form": self.form_class(
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


class RangeDateTimeFilter(admin.FieldListFilter):
    request = None
    parameter_name = None
    template = "unfold/filters/filters_datetime_range.html"
    form_class = RangeDateTimeForm

    def __init__(
        self,
        field: Field,
        request: HttpRequest,
        params: dict[str, str],
        model: type[Model],
        model_admin: ModelAdmin,
        field_path: str,
    ) -> None:
        super().__init__(field, request, params, model, model_admin, field_path)
        if not isinstance(field, DateTimeField):
            raise TypeError(
                f"Class {type(self.field)} is not supported for {self.__class__.__name__}."
            )

        self.request = request
        if self.parameter_name is None:
            self.parameter_name = self.field_path

        if self.parameter_name + "_from_0" in params:
            value = params.pop(self.field_path + "_from_0")
            value = value[0] if isinstance(value, list) else value
            self.used_parameters[self.field_path + "_from_0"] = value

        if self.parameter_name + "_from_1" in params:
            value = params.pop(self.field_path + "_from_1")
            value = value[0] if isinstance(value, list) else value
            self.used_parameters[self.field_path + "_from_1"] = value

        if self.parameter_name + "_to_0" in params:
            value = params.pop(self.field_path + "_to_0")
            value = value[0] if isinstance(value, list) else value
            self.used_parameters[self.field_path + "_to_0"] = value

        if self.parameter_name + "_to_1" in params:
            value = params.pop(self.field_path + "_to_1")
            value = value[0] if isinstance(value, list) else value
            self.used_parameters[self.field_path + "_to_1"] = value

    def expected_parameters(self) -> list[str]:
        return [
            f"{self.parameter_name}_from_0",
            f"{self.parameter_name}_from_1",
            f"{self.parameter_name}_to_0",
            f"{self.parameter_name}_to_1",
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        filters = {}

        date_value_from = self.used_parameters.get(self.parameter_name + "_from_0")
        time_value_from = self.used_parameters.get(self.parameter_name + "_from_1")

        date_value_to = self.used_parameters.get(self.parameter_name + "_to_0")
        time_value_to = self.used_parameters.get(self.parameter_name + "_to_1")

        if date_value_from not in EMPTY_VALUES and time_value_from not in EMPTY_VALUES:
            filters.update(
                {
                    f"{self.parameter_name}__gte": parse_datetime_str(
                        f"{date_value_from} {time_value_from}"
                    ),
                }
            )

        if date_value_to not in EMPTY_VALUES and time_value_to not in EMPTY_VALUES:
            filters.update(
                {
                    f"{self.parameter_name}__lte": parse_datetime_str(
                        f"{date_value_to} {time_value_to}"
                    ),
                }
            )

        try:
            return queryset.filter(**filters)
        except (ValueError, ValidationError):
            return None

    def choices(self, changelist: ChangeList) -> tuple[dict[str, Any], ...]:
        return (
            {
                "request": self.request,
                "parameter_name": self.parameter_name,
                "form": self.form_class(
                    name=self.parameter_name,
                    data={
                        self.parameter_name + "_from_0": self.used_parameters.get(
                            self.parameter_name + "_from_0"
                        ),
                        self.parameter_name + "_from_1": self.used_parameters.get(
                            self.parameter_name + "_from_1"
                        ),
                        self.parameter_name + "_to_0": self.used_parameters.get(
                            self.parameter_name + "_to_0"
                        ),
                        self.parameter_name + "_to_1": self.used_parameters.get(
                            self.parameter_name + "_to_1"
                        ),
                    },
                ),
            },
        )
