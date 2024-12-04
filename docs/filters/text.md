---
title: Text filter
order: 1
description: Text filters for list view.
---

# Text filters

Text input field which allows filtering by the free string submitted by the user. There are two different variants of this filter: `FieldTextFilter` and `TextFilter`.

`FieldTextFilter` requires just a model field name and the filter will make `__icontains` search on this field. There are no other things to configure so the integration in `list_filter` will be just one new row looking like `("model_field_name", FieldTextFilter)`.

In the case of the `TextFilter`, it is needed to write a whole new class inheriting from `TextFilter` with a custom implementation of the `queryset` method and the `parameter_name` attribute. This attribute will be a representation of the search query parameter name in URI. The benefit of the `TextFilter` is the possibility of writing complex queries.

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
