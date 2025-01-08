---
title: ArrayWidget
order: 1
description: ArrayWidget for ArrayField
---

# Unfold widget ArrayWidget

```python
# settings.py

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.forms",
]
```

Below you can see how to use ArrayWidget in your admin class. In this example all `ArrayField` fields will use `ArrayWidget` to render input field. In case `choices` are provided for the widget, dropdown list will be used instead of text input.

```python
# admin.py

from django.contrib import admin
from django.contrib.postgres.fields import ArrayField
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import ArrayWidget


@admin.register(MyModel)
class CustomAdminClass(ModelAdmin):
    formfield_overrides = {
        ArrayField: {
            "widget": ArrayWidget,
        }
    }
```
