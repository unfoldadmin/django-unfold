from unfold.contrib.filters.admin.dropdown_filters import (
    MultipleRelatedDropdownFilter,
    RelatedDropdownFilter,
)
from unfold.contrib.filters.admin.mixins import AutocompleteMixin, MultiValueMixin
from unfold.contrib.filters.forms import AutocompleteDropdownForm


class AutocompleteSelectFilter(AutocompleteMixin, RelatedDropdownFilter):
    form_class = AutocompleteDropdownForm


class AutocompleteSelectMultipleFilter(
    MultiValueMixin, AutocompleteMixin, MultipleRelatedDropdownFilter
):
    form_class = AutocompleteDropdownForm
