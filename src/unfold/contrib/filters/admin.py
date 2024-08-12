from typing import Any, Dict, List, Optional, Tuple, Type

from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.core.validators import EMPTY_VALUES
from django.db.models import Max, Min, Model, QuerySet
from django.db.models.fields import (
    AutoField,
    DateField,
    DateTimeField,
    DecimalField,
    Field,
    FloatField,
    IntegerField,
)
from django.forms import ValidationError
from django.http import HttpRequest
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _

from .forms import (
    DropdownForm,
    RangeDateForm,
    RangeDateTimeForm,
    RangeNumericForm,
    SearchForm,
    SingleNumericForm,
    SliderNumericForm,
)


class ValueMixin:
    def value(self) -> Optional[str]:
        return (
            self.lookup_val[0]
            if self.lookup_val not in EMPTY_VALUES
            and isinstance(self.lookup_val, List)
            and len(self.lookup_val) > 0
            else self.lookup_val
        )


class MultiValueMixin:
    def value(self) -> Optional[List[str]]:
        return (
            self.lookup_val
            if self.lookup_val not in EMPTY_VALUES
            and isinstance(self.lookup_val, List)
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


class TextFilter(admin.SimpleListFilter):
    template = "unfold/filters/filters_field.html"
    form_class = SearchForm

    def has_output(self) -> bool:
        return True

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> Tuple:
        return ()

    def choices(self, changelist: ChangeList) -> Tuple[Dict[str, Any], ...]:
        return (
            {
                "form": self.form_class(
                    name=self.parameter_name,
                    label=_("By {}").format(self.title),
                    data={self.parameter_name: self.value()},
                ),
            },
        )


class FieldTextFilter(ValueMixin, admin.FieldListFilter):
    template = "unfold/filters/filters_field.html"
    form_class = SearchForm

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = f"{field_path}__icontains"
        self.lookup_val = params.get(self.lookup_kwarg)
        super().__init__(field, request, params, model, model_admin, field_path)

    def expected_parameters(self) -> List[str]:
        return [self.lookup_kwarg]

    def choices(self, changelist: ChangeList) -> Tuple[Dict[str, Any], ...]:
        return (
            {
                "form": self.form_class(
                    label=_("By {}").format(self.title),
                    name=self.lookup_kwarg,
                    data={self.lookup_kwarg: self.value()},
                ),
            },
        )


class DropdownFilter(admin.SimpleListFilter):
    template = "unfold/filters/filters_field.html"
    form_class = DropdownForm
    all_option = ["", _("All")]

    def choices(self, changelist: ChangeList) -> Tuple[Dict[str, Any], ...]:
        return (
            {
                "form": self.form_class(
                    label=_("By {}").format(self.title),
                    name=self.parameter_name,
                    choices=[self.all_option, *self.lookup_choices],
                    data={self.parameter_name: self.value()},
                    multiple=self.multiple if hasattr(self, "multiple") else False,
                ),
            },
        )


class MultipleDropdownFilter(DropdownFilter):
    multiple = True

    def __init__(self, request, params, model, model_admin):
        self.request = request
        super().__init__(request, params, model, model_admin)

    def value(self):
        return self.request.GET.getlist(self.parameter_name)


class ChoicesDropdownFilter(ValueMixin, DropdownMixin, admin.ChoicesFieldListFilter):
    def choices(self, changelist: ChangeList):
        choices = [self.all_option, *self.field.flatchoices]

        yield {
            "form": self.form_class(
                label=_("By {}").format(self.title),
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: self.value()},
                multiple=self.multiple if hasattr(self, "multiple") else False,
            ),
        }


class MultipleChoicesDropdownFilter(MultiValueMixin, ChoicesDropdownFilter):
    multiple = True


class RelatedDropdownFilter(ValueMixin, DropdownMixin, admin.RelatedFieldListFilter):
    def choices(self, changelist: ChangeList):
        yield {
            "form": self.form_class(
                label=_("By {}").format(self.title),
                name=self.lookup_kwarg,
                choices=[self.all_option, *self.lookup_choices],
                data={self.lookup_kwarg: self.value()},
                multiple=self.multiple if hasattr(self, "multiple") else False,
            ),
        }


class MultipleRelatedDropdownFilter(MultiValueMixin, RelatedDropdownFilter):
    multiple = True


class SingleNumericFilter(admin.FieldListFilter):
    request = None
    parameter_name = None
    template = "unfold/filters/filters_numeric_single.html"

    def __init__(
        self,
        field: Field,
        request: HttpRequest,
        params: Dict[str, str],
        model: Type[Model],
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

    def expected_parameters(self) -> List[Optional[str]]:
        return [self.parameter_name]

    def choices(self, changelist: ChangeList) -> Tuple[Dict[str, Any], ...]:
        return (
            {
                "request": self.request,
                "parameter_name": self.parameter_name,
                "form": SingleNumericForm(
                    name=self.parameter_name, data={self.parameter_name: self.value()}
                ),
            },
        )


class RangeNumericMixin:
    request = None
    parameter_name = None
    template = "unfold/filters/filters_numeric_range.html"

    def init_used_parameters(self, params: Dict[str, Any]) -> None:
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

    def expected_parameters(self) -> List[str]:
        return [
            f"{self.parameter_name}_from",
            f"{self.parameter_name}_to",
        ]

    def choices(self, changelist: ChangeList) -> Tuple[Dict[str, Any], ...]:
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


class RangeNumericListFilter(RangeNumericMixin, admin.SimpleListFilter):
    def __init__(
        self,
        request: HttpRequest,
        params: Dict[str, str],
        model: Type[Model],
        model_admin: ModelAdmin,
    ) -> None:
        super().__init__(request, params, model, model_admin)
        if not self.parameter_name:
            raise ValueError("Parameter name cannot be None")

        self.request = request
        self.init_used_parameters(params)

    def lookups(
        self, request: HttpRequest, model_admin: ModelAdmin
    ) -> Tuple[Tuple[str, str], ...]:
        return (("dummy", "dummy"),)


class RangeNumericFilter(RangeNumericMixin, admin.FieldListFilter):
    def __init__(
        self,
        field: Field,
        request: HttpRequest,
        params: Dict[str, str],
        model: Type[Model],
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
        params: Dict[str, str],
        model: Type[Model],
        model_admin: ModelAdmin,
        field_path: str,
    ) -> None:
        super().__init__(field, request, params, model, model_admin, field_path)

        self.field = field
        self.q = model_admin.get_queryset(request)

    def choices(self, changelist: ChangeList) -> Tuple[Dict[str, Any], ...]:
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


class RangeDateFilter(admin.FieldListFilter):
    request = None
    parameter_name = None
    form_class = RangeDateForm
    template = "unfold/filters/filters_date_range.html"

    def __init__(
        self,
        field: Field,
        request: HttpRequest,
        params: Dict[str, str],
        model: Type[Model],
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

        value_from = self.used_parameters.get(self.parameter_name + "_from", None)
        if value_from not in EMPTY_VALUES:
            filters.update(
                {
                    self.parameter_name + "__gte": self.used_parameters.get(
                        self.parameter_name + "_from", None
                    ),
                }
            )

        value_to = self.used_parameters.get(self.parameter_name + "_to", None)
        if value_to not in EMPTY_VALUES:
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

    def expected_parameters(self) -> List[str]:
        return [
            f"{self.parameter_name}_from",
            f"{self.parameter_name}_to",
        ]

    def choices(self, changelist: ChangeList) -> Tuple[Dict[str, Any], ...]:
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
        params: Dict[str, str],
        model: Type[Model],
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
            self.used_parameters[self.field_path + "_from_0"] = value

        if self.parameter_name + "_from_1" in params:
            value = params.pop(self.field_path + "_from_1")
            self.used_parameters[self.field_path + "_from_1"] = value

        if self.parameter_name + "_to_0" in params:
            value = params.pop(self.field_path + "_to_0")
            self.used_parameters[self.field_path + "_to_0"] = value

        if self.parameter_name + "_to_1" in params:
            value = params.pop(self.field_path + "_to_1")
            self.used_parameters[self.field_path + "_to_1"] = value

    def expected_parameters(self) -> List[str]:
        return [
            f"{self.parameter_name}_from_0",
            f"{self.parameter_name}_from_1",
            f"{self.parameter_name}_to_0",
            f"{self.parameter_name}_to_1",
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        filters = {}

        date_value_from = self.used_parameters.get(
            self.parameter_name + "_from_0", None
        )
        time_value_from = self.used_parameters.get(
            self.parameter_name + "_from_1", None
        )
        date_value_to = self.used_parameters.get(self.parameter_name + "_to_0", None)
        time_value_to = self.used_parameters.get(self.parameter_name + "_to_1", None)

        if date_value_from not in EMPTY_VALUES and time_value_from not in EMPTY_VALUES:
            filters.update(
                {
                    f"{self.parameter_name}__gte": parse_datetime(
                        f"{date_value_from}T{time_value_from}"
                    ),
                }
            )

        if date_value_to not in EMPTY_VALUES and time_value_to not in EMPTY_VALUES:
            filters.update(
                {
                    f"{self.parameter_name}__lte": parse_datetime(
                        f"{date_value_to}T{time_value_to}"
                    ),
                }
            )

        try:
            return queryset.filter(**filters)
        except (ValueError, ValidationError):
            return None

    def choices(self, changelist: ChangeList) -> Tuple[Dict[str, Any], ...]:
        return (
            {
                "request": self.request,
                "parameter_name": self.parameter_name,
                "form": self.form_class(
                    name=self.parameter_name,
                    data={
                        self.parameter_name + "_from_0": self.used_parameters.get(
                            self.parameter_name + "_from_0", None
                        ),
                        self.parameter_name + "_from_1": self.used_parameters.get(
                            self.parameter_name + "_from_1", None
                        ),
                        self.parameter_name + "_to_0": self.used_parameters.get(
                            self.parameter_name + "_to_0", None
                        ),
                        self.parameter_name + "_to_1": self.used_parameters.get(
                            self.parameter_name + "_to_1", None
                        ),
                    },
                ),
            },
        )
