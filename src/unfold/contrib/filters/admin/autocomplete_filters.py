from unfold.contrib.filters.admin.dropdown_filters import (
    MultipleRelatedDropdownFilter,
    RelatedDropdownFilter,
)
from unfold.contrib.filters.admin.mixins import AutocompleteMixin


class AutocompleteSelectFilter(RelatedDropdownFilter, AutocompleteMixin):
    pass


class AutocompleteSelectMultipleFilter(
    MultipleRelatedDropdownFilter, AutocompleteMixin
):
    pass
