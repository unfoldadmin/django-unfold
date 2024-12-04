---
title: Numeric filter
order: 4
description: Numeric filters for list view.
---

# Numeric filters

Currently, Unfold implements numeric filters inside `unfold.contrib.filters` application. In order to use these filters, it is required to add this application into `INSTALLED_APPS` in `settings.py` right after `unfold` application.

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
