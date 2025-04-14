from collections.abc import Generator
from typing import Any

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from unfold.contrib.filters.admin.mixins import (
    ChoicesMixin,
    MultiValueMixin,
    ValueMixin,
)
from unfold.contrib.filters.forms import CheckboxForm, HorizontalRadioForm, RadioForm


class RadioFilter(admin.SimpleListFilter):
    template = "unfold/filters/filters_field.html"
    form_class = RadioForm
    all_option = ["", _("All")]

    def choices(self, changelist: ChangeList) -> tuple[dict[str, Any], ...]:
        add_facets = getattr(changelist, "add_facets", False)
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None
        choices = []

        if self.all_option:
            choices = [self.all_option]

        if add_facets:
            for i, (lookup, title) in enumerate(self.lookup_choices):
                if (count := facet_counts.get(f"{i}__c", -1)) != -1:
                    title = f"{title} ({count})"
                else:
                    title = f"{title} (-)"

                choices.append((lookup, title))
        else:
            choices.extend(self.lookup_choices)

        return (
            {
                "form": self.form_class(
                    label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                    name=self.parameter_name,
                    choices=choices,
                    data={self.parameter_name: self.value()},
                ),
            },
        )


class CheckboxFilter(RadioFilter):
    form_class = CheckboxForm
    all_option = None

    def value(self) -> list[Any]:
        return self.request.GET.getlist(self.parameter_name)


class ChoicesRadioFilter(ValueMixin, ChoicesMixin, admin.ChoicesFieldListFilter):
    form_class = RadioForm
    all_option = ["", _("All")]


class ChoicesCheckboxFilter(
    MultiValueMixin, ChoicesMixin, admin.ChoicesFieldListFilter
):
    form_class = CheckboxForm
    all_option = None


class BooleanRadioFilter(ValueMixin, admin.BooleanFieldListFilter):
    template = "unfold/filters/filters_field.html"
    form_class = HorizontalRadioForm
    all_option = ["", _("All")]

    def choices(self, changelist: ChangeList) -> Generator[dict[str, Any], None, None]:
        add_facets = getattr(changelist, "add_facets", False)
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None

        if add_facets:
            choices = [
                self.all_option,
                *[
                    ("1", f"{_('Yes')} ({facet_counts['true__c']})"),
                    ("0", f"{_('No')} ({facet_counts['false__c']})"),
                ],
            ]
        else:
            choices = [
                self.all_option,
                *[
                    ("1", _("Yes")),
                    ("0", _("No")),
                ],
            ]

        yield {
            "form": self.form_class(
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: self.value()},
            ),
        }


class RelatedCheckboxFilter(MultiValueMixin, admin.RelatedFieldListFilter):
    template = "unfold/filters/filters_field.html"
    form_class = CheckboxForm

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.value() not in EMPTY_VALUES:
            return super().queryset(request, queryset)

        return queryset

    def choices(self, changelist: ChangeList) -> Generator[dict[str, Any], None, None]:
        add_facets = getattr(changelist, "add_facets", False)
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None

        if add_facets:
            choices = []

            for pk_val, val in self.lookup_choices:
                count = facet_counts[f"{pk_val}__c"]
                choice = (pk_val, f"{val} ({count})")
                choices.append(choice)
        else:
            choices = self.lookup_choices

        yield {
            "form": self.form_class(
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: self.value()},
            ),
        }


class AllValuesCheckboxFilter(MultiValueMixin, admin.AllValuesFieldListFilter):
    template = "unfold/filters/filters_field.html"
    form_class = CheckboxForm

    def choices(self, changelist: ChangeList) -> Generator[dict[str, Any], None, None]:
        add_facets = getattr(changelist, "add_facets", False)
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None

        if add_facets:
            choices = []

            for i, val in enumerate(self.lookup_choices):
                count = facet_counts[f"{i}__c"]
                choice = (val, f"{val} ({count})")
                choices.append(choice)
        else:
            choices = [[val, val] for _i, val in enumerate(self.lookup_choices)]

        if len(choices) == 0:
            return

        yield {
            "form": self.form_class(
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: self.value()},
            ),
        }
