---
title: Autocomplete filter
order: 5
description: Autocomplete filters for changelist view.
---

# Autocomplete filters

Unfold provides two different types of autocomplete filters: `AutocompleteSelectFilter` and `AutocompleteSelectMultipleFilter`. Both of them are implemented in `unfold.contrib.filters` so make sure this app is in your `INSTALLED_APPS` in `settings.py`.

All the referenced fields must be `ForeignKey` or `ManyToManyField` fields and the same time the referenced admin model must have defined `search_fields` attribute otherwise the application will raise an error.

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
