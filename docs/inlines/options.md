---
title: Inline options
order: 1
description: Customize Django Unfold inline options including title customization, title row visibility, and other configuration settings for enhanced admin interface functionality.
---

# Available options for Unfold inlines

## Custom inline title

By default, each inline row's title is derived from the model's `__str__` implementation. However, Unfold provides the ability to customize this title specifically for inlines by implementing a `get_inline_title` method on the model. This method can return a custom title that will only be used in inline contexts, allowing for more descriptive and context-specific labels.

```python
from django.contrib.auth.models import User
from unfold.admin import TabularInline


class User(models.Model):
    # fields, meta ...

    def get_inline_title(self):
        return "Custom title"


class MyInline(TabularInline):
    model = User
```

## Hide title row

You can hide the title row for both `StackedInline` and `TabularInline` by setting the `hide_title` attribute to `True`. This feature is particularly useful when you want to create a more compact and streamlined interface. Please note that for `StackedInline`, the delete permission (`can_delete`) must be disabled to hide the title row, as the delete checkbox is contained within it.

```python
# admin.py

from django.contrib.auth.models import User
from unfold.admin import TabularInline


class MyInline(TabularInline):
    model = User
    hide_title = True
```

## Collapsible StackedInline

Unfold enhances the `StackedInline` functionality by introducing a collapsible mode. When enabled, this feature allows you to display multiple records in a space-efficient manner by defaulting to a collapsed state. This is particularly useful when dealing with forms that contain numerous inline entries, as it helps maintain a clean and organized interface.

Key features of collapsible StackedInlines:
- Records are collapsed by default, saving vertical space
- Users can expand individual records as needed
- Records containing validation errors automatically expand to highlight the issues
- The collapsed state is preserved during form submission
- Each record can be independently expanded or collapsed

To implement this feature, simply set the `collapsible` attribute to `True` in your StackedInline class:

```python
from django.contrib.auth.models import User
from unfold.admin import StackedInline


class User(models.Model):
    inlines = [SomeInline]

class SomeInline(StackedInline):
    collapsible = True
```
