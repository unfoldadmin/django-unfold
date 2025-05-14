---
title: Inline options
order: 1
description: Customize Django Unfold inline options including title customization, title row visibility, and other configuration settings for enhanced admin interface functionality.
---

# Available options for Unfold inlines

By default, each inline row's title is derived from the model's `__str__` implementation. However, Unfold provides the ability to customize this title specifically for inlines by implementing a `get_inline_title` method on the model, which can return a custom title that will only be used in inline contexts.

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

You can hide the title row for both `StackedInline` and `TabularInline` by setting the `hide_title` attribute to `True`. Note that for `StackedInline`, the delete permission (`can_delete`) must be disabled to hide the title row since the delete checkbox is contained within it.

```python
# admin.py

from django.contrib.auth.models import User
from unfold.admin import TabularInline


class MyInline(TabularInline):
    model = User
    hide_title = True
```
