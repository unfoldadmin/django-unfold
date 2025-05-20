---
title: Autocomplete filter
order: 5
description: Enhance your Django admin interface with Unfold's autocomplete filters, featuring single and multiple selection capabilities for ForeignKey and ManyToManyField relationships. Learn how to implement and configure autocomplete filtering with search functionality for improved data management.
---

# Autocomplete filters

Unfold enhances Django's filtering capabilities by providing two distinct types of autocomplete filters: `AutocompleteSelectFilter` for single selection and `AutocompleteSelectMultipleFilter` for multiple selections. Both filters are implemented within the `unfold.contrib.filters` package, so you'll need to ensure this app is properly included in your `INSTALLED_APPS` configuration within `settings.py`.

For these filters to work correctly, there are two key requirements: First, the fields you want to filter must be either `ForeignKey` or `ManyToManyField` relationships. Second, the referenced admin model must have the `search_fields` attribute properly defined to enable the search functionality. If either of these requirements is not met, the application will raise an error to alert you of the misconfiguration.

[![Autocomplete select filter](/static/docs/filters/autocomplete-select-filter.webp)](/static/docs/filters/autocomplete-select-filter.webp)

```python
# admin.py

from django.contrib import admin
from django.contrib.auth.models import User

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    AutocompleteSelectFilter,
    AutocompleteSelectMultipleFilter
)

@admin.register(User)
class YourModelAdmin(ModelAdmin):
    list_filter = (
        # Autocomplete filter
        ["other_model_field", AutocompleteSelectFilter],

        # Autocomplete multiple filter
        ["other_multiple_model_field", AutocompleteSelectMultipleFilter],
    )

class OtherModelAdmin(ModelAdmin):
    search_fields = ["name"]
```
