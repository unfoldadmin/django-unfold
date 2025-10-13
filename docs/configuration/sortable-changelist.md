---
title: Sortable changelist
order: 10
description: Enable sortable changelists in Django Unfold for drag-and-drop record reordering directly in the admin list view.
---

# Sortable changelist

Django Unfold supports sortable changelists, enabling intuitive drag-and-drop reordering of records directly within the changelist (list view) of the admin interface.

## Requirements

To enable sortable functionality on the changelist page:

- Your model must include a dedicated ordering field. This field should be a `PositiveIntegerField` with `db_index=True` for optimal database performance.
- The ordering field must be available in the database and included in your model's `Meta.ordering` or set via queryset ordering.
- Enable `ordering_field` on your `ModelAdmin` and set `hide_ordering_field=True` if you want to hide the field from the list display.

## Limitations

- Sorting is only possible among records displayed on the current page. Records cannot be reordered across multiple pages due to pagination constraints.
- Bulk editing and reordering should be completed and saved before navigating to another page to avoid losing changes.

## Example Configuration


```python
# models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

class MyModel(models.Model):
    weight = models.PositiveIntegerField(_("weight"), default=0, db_index=True)

    class Meta:
        ordering = ["weight"]
```

```python
# admin.py

from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import MyModel

@admin.register(MyModel)
class SomeAdmin(ModelAdmin):
    ordering_field = "weight"
    hide_ordering_field = True  # default: False
```
