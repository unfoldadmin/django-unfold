from collections.abc import Iterator
from typing import Any

from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.core.validators import EMPTY_VALUES
from django.db.models import Field, Model, QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from unfold.contrib.filters.admin.mixins import (
    DropdownMixin,
    MultiValueMixin,
    ValueMixin,
)
from unfold.contrib.filters.forms import DropdownForm


class DropdownFilter(admin.SimpleListFilter):
    template = "unfold/filters/filters_field.html"
    form_class = DropdownForm
    all_option = ["", _("All")]

    def choices(self, changelist: ChangeList) -> Iterator:
        add_facets = getattr(changelist, "add_facets", False)
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None
        choices = [self.all_option] if self.all_option else []

        for i, choice in enumerate(self.lookup_choices):
            if add_facets and facet_counts:
                count = facet_counts[f"{i}__c"]
                choices.append((choice[0], f"{choice[1]} ({count})"))
            else:
                choices.append(choice)

        yield {
            "form": self.form_class(
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.parameter_name,
                choices=choices,
                data={self.parameter_name: self.value()},
                multiple=self.multiple if hasattr(self, "multiple") else False,
            ),
        }


class MultipleDropdownFilter(DropdownFilter):
    multiple = True
    used_parameters: dict[str, list[str]]

    def __init__(
        self,
        request: HttpRequest,
        params: dict[str, Any],
        model: type[Model],
        model_admin: ModelAdmin,
    ) -> None:
        self.request = request
        super().__init__(request, params, model, model_admin)

        if (
            self.parameter_name is not None
            and isinstance(self.parameter_name, str)
            and self.parameter_name in self.request.GET
        ):
            self.used_parameters[self.parameter_name] = self.request.GET.getlist(
                self.parameter_name
            )


class ChoicesDropdownFilter(ValueMixin, DropdownMixin, admin.ChoicesFieldListFilter):
    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet | None:
        if self.value() not in EMPTY_VALUES:
            return super().queryset(request, queryset)

        return queryset

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
                data={self.lookup_kwarg: self.value()},
                multiple=self.multiple if hasattr(self, "multiple") else False,
            ),
        }


class MultipleChoicesDropdownFilter(MultiValueMixin, ChoicesDropdownFilter):
    multiple = True


class RelatedDropdownFilter(ValueMixin, DropdownMixin, admin.RelatedFieldListFilter):
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
        self.model_admin = model_admin
        self.request = request

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet | None:
        if self.value() not in EMPTY_VALUES:
            return super().queryset(request, queryset)

        return queryset

    def choices(self, changelist: ChangeList) -> Iterator:
        add_facets = getattr(changelist, "add_facets", False)
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None

        if add_facets and facet_counts:
            choices = [self.all_option]

            for pk_val, val in self.lookup_choices:
                count = facet_counts[f"{pk_val}__c"]
                choice = (pk_val, f"{val} ({count})")
                choices.append(choice)
        else:
            choices = [self.all_option, *self.lookup_choices]

        yield {
            "form": self.form_class(
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: self.value()},
                multiple=self.multiple if hasattr(self, "multiple") else False,
            ),
        }


class MultipleRelatedDropdownFilter(MultiValueMixin, RelatedDropdownFilter):
    multiple = True
