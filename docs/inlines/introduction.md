---
title: Introduction to inlines
order: 0
description: Implement and customize Django Unfold's inline classes for enhanced admin interfaces, including stacked and tabular inlines with improved styling and configuration options.
---

# Inlines

Unfold inlines are built upon Django's inline functionality, providing enhanced styling capabilities and additional configuration options. While Django's native inline classes (`StackedInline` and `TabularInline`) will function correctly, they won't match Unfold's default design aesthetic. For the best visual consistency and full feature set, it is strongly recommended to use Unfold's own inline classes instead of the standard Django ones.

```python
# admin.py

from django.contrib import admin
from django.contrib.auth.models import User
from unfold.admin import StackedInline, TabularInline


class MyStackedInline(StackedInline):
    model = User


class MyTabularInline(TabularInline):
    model = User


@admin.register(User)
class UserAdmin(ModelAdmin):
    inlines = [MyStackedInline, MyTabularInline]
```
