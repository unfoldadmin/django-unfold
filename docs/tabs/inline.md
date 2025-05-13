---
title: Inlines tabs
order: 4
description: Learn how to organize Django admin inlines into tabs by using the tab attribute in inline classes, enabling better form organization and user experience in changeform views.
---

# Inlines tabs

Django Unfold allows you to organize inline forms into tab navigation by setting the `tab` attribute to `True` in your inline class definition. This feature is specifically designed for changeform pages, providing a cleaner and more organized interface when dealing with multiple inline forms. Please note that without implementing custom code, it is not possible to add other types of custom tabs to this navigation system. The tab navigation for inlines works independently from the main tab system and is specifically tailored for managing related model instances.

[![Inline Tabs](/static/docs/tabs/inline-tabs.webp)](/static/docs/tabs/inline-tabs.webp)

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
