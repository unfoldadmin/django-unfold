---
title: Text filter
order: 1
description: Implement powerful text-based filtering in Django Unfold's admin interface with FieldTextFilter for simple field searches and TextFilter for complex custom filtering logic, complete with examples and configuration options.
---

# Text filters

The text input field provides a flexible filtering mechanism that allows users to search using any string they input. Unfold offers two distinct variants of this filter: `FieldTextFilter` and `TextFilter`, each serving different use cases.

The `FieldTextFilter` is straightforward to implement, requiring only a model field name. It automatically performs a case-insensitive search (using `__icontains`) on the specified field. Configuration is minimal - you simply need to add a tuple containing the model field name and `FieldTextFilter` to your `list_filter` configuration, like this: `("model_field_name", FieldTextFilter)`.

For more complex filtering requirements, the `TextFilter` offers greater flexibility. To use it, you'll need to create a new class that inherits from `TextFilter` and implement a custom `queryset` method. You'll also need to specify a `parameter_name` attribute, which defines how the search parameter will appear in the URL. The main advantage of `TextFilter` is its ability to handle sophisticated query logic, allowing you to create highly customized filtering behavior.

[![Text filter](/static/docs/filters/text-filter.webp)](/static/docs/filters/text-filter.webp)

```python
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.validators import EMPTY_VALUES
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import TextFilter, FieldTextFilter

class CustomTextFilter(TextFilter):
    title = _("Custom filter")
    parameter_name = "query_param_in_uri"

    def queryset(self, request, queryset):
        if self.value() not in EMPTY_VALUES:
            # Here write custom query
            return queryset.filter(your_field=self.value())

        return queryset


@admin.register(User)
class MyAdmin(ModelAdmin):
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = [
        ("model_charfield", FieldTextFilter),
        CustomTextFilter
    ]
```
