from collections.abc import Generator
from typing import Any

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from unfold.contrib.filters.admin.mixins import MultiValueMixin
from unfold.contrib.filters.forms import CheckboxForm


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
                multiple=self.multiple if hasattr(self, "multiple") else False,
            ),
        }
