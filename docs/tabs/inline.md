---
title: Inlines tabs
order: 4
description: Learn how to organize Django admin inlines into tabs by using the tab attribute in inline classes, enabling better form organization and user experience in changeform views.
---

# Inlines tabs

Inlines can be grouped into tab navigation by specifying `tab` attribute in the inline class. This behavior is enabled on changeform pages and it is not possible to add other custom tabs into tab navigation without writing custom code.

```python
# admin.py

from django.contrib.auth.models import User
from unfold.admin import StackedInline, TabularInline


class MyTabularInline(TabularInline):
    model = User
    tab = True

class MyStackedInline(StackedInline):
    model = User
    tab = True
```
