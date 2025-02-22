---
title: Horizontal layout filter
order: 5
description: Horizontal layout for filter choices in the changelist view.
---

# Horizontal layout filter

Unfold provides a horizontal layout for filter choices in the changelist view. By default, the layout for filter choices is vertical but by providing the `horizontal` attribute set to `True` to the filter class, the layout will be horizontal.

```python
# admin.py

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.admin.filters import ChoicesFieldListFilter

from unfold.admin import ModelAdmin


User = get_user_model()

class HorizontalChoicesFieldListFilter(ChoicesFieldListFilter):
    horizontal = True # Enable horizontal layout


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_filter = (
        ["other_model_field", HorizontalChoicesFieldListFilter],
    )
```
