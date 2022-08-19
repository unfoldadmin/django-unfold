from django.contrib import admin
from django.db.models import Max, Min
from django.db.models.fields import AutoField, DecimalField, FloatField, IntegerField

from .forms import RangeNumericForm, SingleNumericForm, SliderNumericForm


class NumericFilterModelAdmin(admin.ModelAdmin):
    class Media:
        css = {"all": ("js/nouislider.min.css",)}
        js = (
            "js/wNumb.min.js",
            "js/nouislider.min.js",
            "js/admin-numeric-filter.js",
        )


class SingleNumericMixin:
    request = None
    parameter_name = None
    template = "admin/filter_numeric_single.html"

    def prefill_used_parameters(self, params):
        if self.parameter_name in params:
            value = params.pop(self.parameter_name)
            self.used_parameters[self.parameter_name] = value

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{self.parameter_name: self.value()})

    def value(self):
        return self.used_parameters.get(self.parameter_name, None)

    def expected_parameters(self):
        return [self.parameter_name]

    def choices(self, changelist):
        return (
            {
                "request": self.request,
                "parameter_name": self.parameter_name,
                "form": SingleNumericForm(
                    name=self.parameter_name, data={self.parameter_name: self.value()}
                ),
            },
        )


class SingleNumericFilter(SingleNumericMixin, admin.SimpleListFilter):
    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)

        self.request = request
        if not self.parameter_name:
            raise ValueError("Parameter name cannot be None")

        self.prefill_used_parameters(params)

    def lookups(self, request, model_admin):
        return (("dummy", "dummy"),)


class SingleFieldNumericFilter(SingleNumericMixin, admin.FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        if not isinstance(field, (DecimalField, IntegerField, FloatField, AutoField)):
            raise TypeError(
                f"Class {type(self.field)} is not supported for {self.__class__.__name__}."
            )

        self.request = request
        if self.parameter_name is None:
            self.parameter_name = self.field_path

        self.prefill_used_parameters(params)


class RangeNumericMixin:
    request = None
    parameter_name = None
    template = "admin/filter_numeric_range.html"

    def init_used_parameters(self, params):
        if self.parameter_name + "_from" in params:
            value = params.pop(self.parameter_name + "_from")
            self.used_parameters[self.parameter_name + "_from"] = value

        if self.parameter_name + "_to" in params:
            value = params.pop(self.parameter_name + "_to")
            self.used_parameters[self.parameter_name + "_to"] = value

    def queryset(self, request, queryset):
        filters = {}

        value_from = self.used_parameters.get(self.parameter_name + "_from", None)
        if value_from is not None and value_from != "":
            filters.update(
                {
                    self.parameter_name
                    + "__gte": self.used_parameters.get(
                        self.parameter_name + "_from", None
                    ),
                }
            )

        value_to = self.used_parameters.get(self.parameter_name + "_to", None)
        if value_to is not None and value_to != "":
            filters.update(
                {
                    self.parameter_name
                    + "__lte": self.used_parameters.get(
                        self.parameter_name + "_to", None
                    ),
                }
            )

        return queryset.filter(**filters)

    def expected_parameters(self):
        return [
            f"{self.parameter_name}_from",
            f"{self.parameter_name}_to",
        ]

    def choices(self, changelist):
        return (
            {
                "request": self.request,
                "parameter_name": self.parameter_name,
                "form": RangeNumericForm(
                    name=self.parameter_name,
                    data={
                        self.parameter_name
                        + "_from": self.used_parameters.get(
                            self.parameter_name + "_from", None
                        ),
                        self.parameter_name
                        + "_to": self.used_parameters.get(
                            self.parameter_name + "_to", None
                        ),
                    },
                ),
            },
        )


class RangeNumericFilter(RangeNumericMixin, admin.SimpleListFilter):
    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        if not self.parameter_name:
            raise ValueError("Parameter name cannot be None")

        self.request = request
        self.init_used_parameters(params)

    def lookups(self, request, model_admin):
        return (("dummy", "dummy"),)


class RangeFieldNumericFilter(RangeNumericMixin, admin.FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
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

    template = "admin/filter_numeric_slider.html"
    field = None

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)

        self.field = field
        self.q = model_admin.get_queryset(request)

    def choices(self, changelist):
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
                "form": SliderNumericForm(
                    name=self.parameter_name,
                    data={
                        self.parameter_name
                        + "_from": self.used_parameters.get(
                            self.parameter_name + "_from", min_value
                        ),
                        self.parameter_name
                        + "_to": self.used_parameters.get(
                            self.parameter_name + "_to", max_value
                        ),
                    },
                ),
            },
        )

    def _get_min_step(self, precision):
        result_format = f"{{:.{precision - 1}f}}"
        return float(result_format.format(0) + "1")
