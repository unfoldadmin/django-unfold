---
title: Numeric filter
order: 4
description: Enhance your Django admin interface with Unfold's numeric filtering capabilities, including single field, range, and slider filters for precise data filtering. Learn how to implement and customize various numeric filter types with examples and configuration options.
---

# Numeric filters

Unfold provides numeric filtering capabilities through its `unfold.contrib.filters` application. To utilize these powerful filtering features in your project, you'll need to add this application to your `INSTALLED_APPS` configuration in `settings.py`. Make sure to place it immediately after the `unfold` application to ensure proper functionality and dependency resolution.

[![Numeric filter](/static/docs/filters/numeric-filter.webp)](/static/docs/filters/numeric-filter.webp)

```python
# admin.py

from django.contrib import admin
from django.contrib.auth.models import User

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    RangeNumericListFilter,
    RangeNumericFilter,
    SingleNumericFilter,
    SliderNumericFilter,
)


class CustomSliderNumericFilter(SliderNumericFilter):
    MAX_DECIMALS = 2
    STEP = 10


class CustomRangeNumericListFilter(RangeNumericListFilter):
    parameter_name = "items_count"
    title = "items"


@admin.register(User)
class YourModelAdmin(ModelAdmin):
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = (
        ("field_A", SingleNumericFilter),  # Numeric single field search, __gte lookup
        ("field_B", RangeNumericFilter),  # Numeric range search, __gte and __lte lookup
        ("field_C", SliderNumericFilter),  # Numeric range filter but with slider
        ("field_D", CustomSliderNumericFilter),  # Numeric filter with custom attributes
        CustomRangeNumericListFilter,  # Numeric range search not restricted to a model field
    )

    def get_queryset(self, request):
        return super().get_queryset().annotate(items_count=Count("item", distinct=True))
```
