---
title: Sortable inlines
order: 3
description: Sorting functionality in Django admin for TabularInline and StackedInline.
---

# Sortable inlines

Unfold allows you to sort inlines by adding a `ordering_field` to the inline class. This field will be used to sort the inlines in the admin panel. There is also an option to hide the ordering field from the UI by setting `hide_ordering_field` to `True`.

- The model field used for ordering must be a `PositiveIntegerField` with `db_index=True`
- Sorting newly added records does not work. You need so save new records first and then sort
- The sorting functionality is not available on changelist view.

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

In order to use the sorting functionality, you need to create a model field with a `PositiveIntegerField` type and set `db_index=True` where the Unfold admin will store the sorting order.

```python
# models.py

from django.db import models
from django.utils.translation import gettext_lazy as _


class User(models.Model):
    weight = models.PositiveIntegerField(_("weight"), default=0, db_index=True)
```
