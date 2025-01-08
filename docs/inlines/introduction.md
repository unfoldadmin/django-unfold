---
title: Introduction to inlines
order: 0
description: Custom inline classes for Unfold admin.
---

# Inlines

Unfold inlines are derived from Django inlines, and they are used to add extra styling and configuration options. Native inline classes `StackedInline` and `TabularInline` are going work but the styling will not match default Unfold design thus it is recommended to use inlines derived from Unfold.

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
