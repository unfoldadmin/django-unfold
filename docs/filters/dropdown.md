---
title: Dropdown filter
order: 3
description: Dropdown filters for list view.
---

# Dropdown filters

Dropdown filters will display a select field with a list of options. Unfold contains two types of dropdowns: `ChoicesDropdownFilter` and `RelatedDropdownFilter`.

The difference between them is that `ChoicesDropdownFilter` will collect a list of options based on the `choices` attribute of the model field so most commonly it will be used in combination with `CharField` with specified `choices`.  On the other hand, `RelatedDropdownFilter` needs a one-to-many or many-to-many foreign key to display options.

```python
# admin.py

from django.contrib import admin
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    ChoicesDropdownFilter,
    MultipleChoicesDropdownFilter,
    RelatedDropdownFilter,
    MultipleRelatedDropdownFilter,
    DropdownFilter,
    MultipleDropdownFilter
)


class CustomDropdownFilter(DropdownFilter):
    title = _("Custom dropdown filter")
    parameter_name = "query_param_in_uri"

    def lookups(self, request, model_admin):
        return [
            ["option_1", _("Option 1")],
            ["option_2", _("Option 2")],
        ]

    def queryset(self, request, queryset):
        if self.value() not in EMPTY_VALUES:
            # Here write custom query
            return queryset.filter(your_field=self.value())

        return queryset


@admin.register(User)
class MyAdmin(ModelAdmin):
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = [
        CustomDropdownFilter,
        ("modelfield_with_choices", ChoicesDropdownFilter),
        ("modelfield_with_choices_multiple", MultipleChoicesDropdownFilter),
        ("modelfield_with_foreign_key", RelatedDropdownFilter)
        ("modelfield_with_foreign_key_multiple", MultipleRelatedDropdownFilter)
    ]
```

**Note:** At the moment Unfold does not implement a dropdown with an autocomplete functionality, so it is important not to use dropdowns displaying large datasets.

**Note:** All dropdowns are using Select2 for better UX by default. Native implementation with simple select dropdown is not available.
