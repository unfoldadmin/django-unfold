---
title: Sortable inlines
order: 3
description: Implement sortable inlines in Django Unfold to enable drag-and-drop reordering of inline items, with customizable ordering fields and UI options for both TabularInline and StackedInline components.
---

# Sortable inlines

Django Unfold provides a powerful sorting capability for inlines through the `ordering_field` attribute in the inline class. When specified, this field determines the sorting order of inlines within the admin panel. For enhanced UI customization, you can optionally hide the ordering field from the interface by setting `hide_ordering_field` to `True`.

[![Sortable inlines](/static/docs/inlines/sortable-inlines.webp)](/static/docs/tabs/sortable-inlines.webp)


Important considerations when implementing sortable inlines:

- The model field designated for ordering must be defined as a `PositiveIntegerField` with `db_index=True` for optimal performance
- Sorting functionality is limited to existing records - newly added inline items must first be saved before they can be sorted
- The sorting feature is specifically designed for inline views and is not available in the changelist view
- The ordering field will automatically handle maintaining the correct sequence of items when records are reordered

```python
# admin.py

from unfold.admin import TabularInline
from .models import User


# This works for StackedInline as well
class MyInline(TabularInline):
    model = User
    ordering_field = "weight"
    hide_ordering_field = True
    list_display = ["email", "weight"]  # Weight is mandatory field
```

To enable sorting functionality, create a model field of type `PositiveIntegerField` with `db_index=True`. This field will be used by the Unfold admin to maintain the sorting order of your records.

```python
# models.py

from django.db import models
from django.utils.translation import gettext_lazy as _


class User(models.Model):
    weight = models.PositiveIntegerField(_("weight"), default=0, db_index=True)
```
