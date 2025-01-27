from typing import Any, Dict, List, Tuple

from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from unfold.contrib.filters.admin.mixins import ValueMixin
from unfold.contrib.filters.forms import SearchForm


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
                    label=_("By %(filter_title)s") % {"filter_title": self.title},
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
                    label=_("By %(filter_title)s") % {"filter_title": self.title},
                    name=self.lookup_kwarg,
                    data={self.lookup_kwarg: self.value()},
                ),
            },
        )
