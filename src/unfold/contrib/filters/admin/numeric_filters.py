from typing import Any, Optional

from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.core.validators import EMPTY_VALUES
from django.db.models import Max, Min, Model, QuerySet
from django.db.models.fields import (
    AutoField,
    DecimalField,
    Field,
    FloatField,
    IntegerField,
)
from django.forms import ValidationError
from django.http import HttpRequest

from unfold.contrib.filters.admin.mixins import RangeNumericMixin
from unfold.contrib.filters.forms import SingleNumericForm, SliderNumericForm


class SingleNumericFilter(admin.FieldListFilter):
    request = None
    parameter_name = None
    template = "unfold/filters/filters_numeric_single.html"

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

        if not isinstance(field, (DecimalField, IntegerField, FloatField, AutoField)):
            raise TypeError(
                f"Class {type(self.field)} is not supported for {self.__class__.__name__}."
            )

        self.request = request

        if self.parameter_name is None:
            self.parameter_name = self.field_path

        if self.parameter_name in params:
            value = params.pop(self.parameter_name)
            value = value[0] if isinstance(value, list) else value

            if value not in EMPTY_VALUES:
                self.used_parameters[self.parameter_name] = value

    def queryset(
        self, request: HttpRequest, queryset: QuerySet[Any]
    ) -> Optional[QuerySet]:
        if self.value():
            try:
                return queryset.filter(**{self.parameter_name: self.value()})
            except (ValueError, ValidationError):
                return None

    def value(self) -> Any:
        return self.used_parameters.get(self.parameter_name, None)

    def expected_parameters(self) -> list[Optional[str]]:
        return [self.parameter_name]

    def choices(self, changelist: ChangeList) -> tuple[dict[str, Any], ...]:
        return (
            {
                "request": self.request,
                "parameter_name": self.parameter_name,
                "form": SingleNumericForm(
                    name=self.parameter_name, data={self.parameter_name: self.value()}
                ),
            },
        )


class RangeNumericListFilter(RangeNumericMixin, admin.SimpleListFilter):
    def __init__(
        self,
        request: HttpRequest,
        params: dict[str, str],
        model: type[Model],
        model_admin: ModelAdmin,
    ) -> None:
        super().__init__(request, params, model, model_admin)
        if not self.parameter_name:
            raise ValueError("Parameter name cannot be None")

        self.request = request
        self.init_used_parameters(params)

    def lookups(
        self, request: HttpRequest, model_admin: ModelAdmin
    ) -> tuple[tuple[str, str], ...]:
        return (("dummy", "dummy"),)


class RangeNumericFilter(RangeNumericMixin, admin.FieldListFilter):
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
        if not isinstance(field, (DecimalField, IntegerField, FloatField, AutoField)):
            raise TypeError(
                f"Class {type(self.field)} is not supported for {self.__class__.__name__}."
            )

        self.request = request
        if self.parameter_name is None:
            self.parameter_name = self.field_path

        self.init_used_parameters(params)


class SliderNumericFilter(RangeNumericFilter):
    MAX_DECIMALS = 7
    STEP = None

    template = "unfold/filters/filters_numeric_slider.html"
    field = None
    form_class = SliderNumericForm

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

        self.field = field
        self.q = model_admin.get_queryset(request)

    def choices(self, changelist: ChangeList) -> tuple[dict[str, Any], ...]:
        total = self.q.all().count()
        min_value = self.q.all().aggregate(min=Min(self.parameter_name)).get("min", 0)

        if total > 1:
            max_value = (
                self.q.all().aggregate(max=Max(self.parameter_name)).get("max", 0)
            )
        else:
            max_value = None

        if isinstance(self.field, (FloatField, DecimalField)):
            decimals = self.MAX_DECIMALS
            step = self.STEP if self.STEP else self._get_min_step(self.MAX_DECIMALS)
        else:
            decimals = 0
            step = self.STEP if self.STEP else 1

        return (
            {
                "decimals": decimals,
                "step": step,
                "parameter_name": self.parameter_name,
                "request": self.request,
                "min": min_value,
                "max": max_value,
                "value_from": self.used_parameters.get(
                    self.parameter_name + "_from", min_value
                ),
                "value_to": self.used_parameters.get(
                    self.parameter_name + "_to", max_value
                ),
                "form": self.form_class(
                    name=self.parameter_name,
                    data={
                        self.parameter_name + "_from": self.used_parameters.get(
                            self.parameter_name + "_from", min_value
                        ),
                        self.parameter_name + "_to": self.used_parameters.get(
                            self.parameter_name + "_to", max_value
                        ),
                    },
                ),
            },
        )

    def _get_min_step(self, precision: int) -> float:
        result_format = f"{{:.{precision - 1}f}}"
        return float(result_format.format(0) + "1")
