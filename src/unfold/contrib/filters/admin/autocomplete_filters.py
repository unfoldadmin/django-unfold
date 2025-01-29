from unfold.contrib.filters.admin.dropdown_filters import (
    MultipleRelatedDropdownFilter,
    RelatedDropdownFilter,
)
from unfold.contrib.filters.admin.mixins import AutocompleteMixin
from unfold.contrib.filters.forms import AutocompleteDropdownForm


class AutocompleteSelectFilter(AutocompleteMixin, RelatedDropdownFilter):
    form_class = AutocompleteDropdownForm


class AutocompleteSelectMultipleFilter(
    MultipleRelatedDropdownFilter, AutocompleteMixin
):
    form_class = AutocompleteDropdownForm
