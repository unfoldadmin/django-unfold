---
title: Inline options
order: 1
description: All available options for inlines.
---

# Available options for Unfold inlines

By default, the title available for each inline row is coming from the `__str__` implementation of the model. Unfold allows you to override this title by implementing `get_inline_title` on the model which can return your own custom title just for the inline.

```python
from django.contrib.auth.models import User
from unfold.admin import TabularInline


class User(models.Model):
    # fiels, meta ...

    def get_inline_title(self):
        return "Custom title"


class MyInline(TabularInline):
    model = User
```

## Hide title row

By applying `hide_title` attribute set to `True`, it is possible to hide the title row which is available for `StackedInline` or `TabularInline`. For `StackedInline` it is required to have disabled delete permission `can_delete` to be able to hide the title row, because the checkbox with the delete action is inside this title.

```python
# admin.py

from django.contrib.auth.models import User
from unfold.admin import TabularInline


class MyInline(TabularInline):
    model = User
    hide_title = True
```
