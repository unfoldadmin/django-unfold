from django.contrib.admin.views.main import ChangeList
from django.utils.translation import gettext_lazy as _

from unfold.contrib.filters.admin.dropdown_filters import (
    MultipleRelatedDropdownFilter,
    RelatedDropdownFilter,
)
from unfold.contrib.filters.forms import AutocompleteDropdownForm


class AutocompleteSelectFilter(RelatedDropdownFilter):
    form_class = AutocompleteDropdownForm

    def choices(self, changelist: ChangeList):
        yield {
            "form": self.form_class(
                request=self.request,
                label=_("By %(filter_title)s") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=(),
                field=self.field,
                model_admin=self.model_admin,
                data={self.lookup_kwarg: self.value()},
                multiple=self.multiple if hasattr(self, "multiple") else False,
            ),
        }


class AutocompleteSelectMultipleFilter(MultipleRelatedDropdownFilter):
    form_class = AutocompleteDropdownForm

    def choices(self, changelist: ChangeList):
        yield {
            "form": self.form_class(
                request=self.request,
                label=_("By %(filter_title)s") % {"filter_title": self.title},
                name=self.lookup_kwarg,
                choices=(),
                field=self.field,
                model_admin=self.model_admin,
                data={self.lookup_kwarg: self.value()},
                multiple=self.multiple if hasattr(self, "multiple") else False,
            ),
        }
