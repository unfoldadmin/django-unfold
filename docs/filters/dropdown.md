---
title: Dropdown filter
order: 3
description: Enhance your Django admin interface with Unfold's dropdown filters, featuring choices-based and relationship-based filtering options. Learn how to implement and customize dropdown filters for improved data filtering and management.
---

# Dropdown filters

Dropdown filters enhance your Django admin interface by providing select fields with customizable lists of options. Unfold offers two primary types of dropdown filters: `ChoicesDropdownFilter` and `RelatedDropdownFilter`, each serving different use cases.

The key distinction between these filters lies in how they source their options. The `ChoicesDropdownFilter` generates its list of options by utilizing the `choices` attribute defined on a model field. This makes it particularly well-suited for use with `CharField` fields that have predefined choices. In contrast, the `RelatedDropdownFilter` is designed to work with one-to-many or many-to-many foreign key relationships, automatically populating the dropdown with related model instances. This flexibility allows you to create intuitive filtering interfaces based on your data model structure.

[![Related dropdown filter](/static/docs/filters/related-dropdown-filter.webp)](/static/docs/filters/related-dropdown-filter.webp)

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
