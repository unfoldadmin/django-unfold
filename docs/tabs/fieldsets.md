---
title: Fieldsets tabs
order: 3
description: Learn how to organize Django admin fieldsets into tabs for better form organization and user experience by using CSS classes to group related fields into tabbed navigation.
---

# Fieldsets tabs

When the change form contains a lot of fieldsets, sometimes it is better to group them into tabs so it will not be needed to scroll. To mark a fieldset for tab navigation it is required to add a `tab` CSS class to the fieldset. Once the fieldset contains `tab` class it will be recognized in a template and grouped into tab navigation. Each tab must contain its name. If the name is not available, it will be not included in the tab navigation.

```python
# admin.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from .models import MyModel


@admin.register(MyModel)
class MyModelAdmin(ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": [
                    "field_1",
                    "field_2",
                ],
            },
        ),
        (
            _("Tab 1"),
            {
                "classes": ["tab"],
                "fields": [
                    "field_3",
                    "field_4",
                ],
            },
        ),
        (
            _("Tab 2"),
            {
                "classes": ["tab"],
                "fields": [
                    "field_5",
                    "field_6",
                ],
            },
        ),
    )
```

**Note:** These tabs are not displayed at the top of the page as other tabs. They are shown in the main content area as one fieldset with smaller tab navigation.
