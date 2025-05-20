---
title: Datetime filter
order: 2
description: Enhance your Django admin interface with Unfold's datetime filtering capabilities, including date and datetime range filters for precise data filtering. Learn how to implement and customize date-based filters with examples and configuration options.
---

# Datetime filters

Unfold offers two powerful datetime filtering options: the `RangeDateFilter` for date-only fields and the `RangeDateTimeFilter` for datetime fields. These filters are both implemented within the `unfold.contrib.filters` application, so you'll need to ensure this application is included in your project's `INSTALLED_APPS` configuration within `settings.py` for proper functionality.

[![Datetime filter](/static/docs/filters/datetime-filter.webp)](/static/docs/filters/datetime-filter.webp)

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
