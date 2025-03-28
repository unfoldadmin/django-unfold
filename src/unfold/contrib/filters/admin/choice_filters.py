from collections.abc import Generator
from typing import Any

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from unfold.contrib.filters.admin.mixins import MultiValueMixin, ValueMixin
from unfold.contrib.filters.forms import CheckboxForm, HorizontalRadioForm, RadioForm


class RadioFilter(admin.SimpleListFilter):
    template = "unfold/filters/filters_field.html"
    form_class = RadioForm
    all_option = ["", _("All")]

    def choices(self, changelist: ChangeList) -> tuple[dict[str, Any], ...]:
        if self.all_option:
            choices = [self.all_option, *self.lookup_choices]
        else:
            choices = self.lookup_choices

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


class ChoicesMixin:
    template = "unfold/filters/filters_field.html"

    def choices(self, changelist: ChangeList) -> Generator[dict[str, Any], None, None]:
        if self.all_option:
            choices = [self.all_option, *self.field.flatchoices]
        else:
            choices = self.field.flatchoices

        yield {
            "form": self.form_class(
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: self.value()},
            ),
        }


class ChoicesRadioFilter(ValueMixin, ChoicesMixin, admin.ChoicesFieldListFilter):
    form_class = RadioForm
    all_option = ["", _("All")]


class ChoicesCheckboxFilter(ValueMixin, ChoicesMixin, admin.ChoicesFieldListFilter):
    form_class = CheckboxForm
    all_option = None


class BooleanRadioFilter(ValueMixin, admin.BooleanFieldListFilter):
    template = "unfold/filters/filters_field.html"
    form_class = HorizontalRadioForm
    all_option = ["", _("All")]

    def choices(self, changelist: ChangeList) -> Generator[dict[str, Any], None, None]:
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
        yield {
            "form": self.form_class(
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=self.lookup_choices,
                data={self.lookup_kwarg: self.value()},
            ),
        }


class AllValuesCheckboxFilter(MultiValueMixin, admin.AllValuesFieldListFilter):
    template = "unfold/filters/filters_field.html"
    form_class = CheckboxForm

    def choices(self, changelist: ChangeList) -> Generator[dict[str, Any], None, None]:
        choices = [[i, val] for i, val in enumerate(self.lookup_choices)]

        if len(choices) == 0:
            return

        yield {
            "form": self.form_class(
                label=_(" By %(filter_title)s ") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=[[i, val] for i, val in enumerate(self.lookup_choices)],
                data={self.lookup_kwarg: self.value()},
            ),
        }
