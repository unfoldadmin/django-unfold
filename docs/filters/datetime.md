---
title: Datetime filter
order: 2
description: Date and datetime filters for list view.
---

# Datetime filters

Unfold provides two different types of datetime filters: `RangeDateFilter` and `RangeDateTimeFilter`. Both of them are implemented in `unfold.contrib.filters` so make sure this app is in your `INSTALLED_APPS` in `settings.py`.

```python
# admin.py

from django.contrib import admin
from django.contrib.auth.models import User

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter, RangeDateTimeFilter


@admin.register(User)
class YourModelAdmin(ModelAdmin):
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = (
        ("field_E", RangeDateFilter),  # Date filter
        ("field_F", RangeDateTimeFilter),  # Datetime filter
    )
```
