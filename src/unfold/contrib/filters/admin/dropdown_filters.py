from typing import Any, Dict, Generator, List, Tuple, Type

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Field, Model
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
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

    def choices(self, changelist: ChangeList) -> Tuple[Dict[str, Any], ...]:
        return (
            {
                "form": self.form_class(
                    label=_("By %(filter_title)s") % {"filter_title": self.title},
                    name=self.parameter_name,
                    choices=[self.all_option, *self.lookup_choices],
                    data={self.parameter_name: self.value()},
                    multiple=self.multiple if hasattr(self, "multiple") else False,
                ),
            },
        )


class MultipleDropdownFilter(DropdownFilter):
    multiple = True

    def __init__(
        self,
        request: HttpRequest,
        params: Dict[str, Any],
        model: Type[Model],
        model_admin: ModelAdmin,
    ) -> None:
        self.request = request
        super().__init__(request, params, model, model_admin)

    def value(self) -> List[Any]:
        return self.request.GET.getlist(self.parameter_name)


class ChoicesDropdownFilter(ValueMixin, DropdownMixin, admin.ChoicesFieldListFilter):
    def choices(self, changelist: ChangeList) -> Generator[Dict[str, Any], None, None]:
        choices = [self.all_option, *self.field.flatchoices]

        yield {
            "form": self.form_class(
                label=_("By %(filter_title)s") % {"filter_title": self.title},
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
        params: Dict[str, str],
        model: Type[Model],
        model_admin: ModelAdmin,
        field_path: str,
    ) -> None:
        super().__init__(field, request, params, model, model_admin, field_path)
        self.model_admin = model_admin

    def choices(self, changelist: ChangeList) -> Generator[Dict[str, Any], None, None]:
        yield {
            "form": self.form_class(
                label=_("By %(filter_title)s") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=[self.all_option, *self.lookup_choices],
                data={self.lookup_kwarg: self.value()},
                multiple=self.multiple if hasattr(self, "multiple") else False,
            ),
        }


class MultipleRelatedDropdownFilter(MultiValueMixin, RelatedDropdownFilter):
    multiple = True
