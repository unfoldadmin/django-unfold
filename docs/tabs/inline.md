---
title: Inlines tabs
order: 4
description: Learn how to organize Django admin inlines into tabs by using the tab attribute in inline classes, enabling better form organization and user experience in changeform views.
---

# Inlines tabs

Django Unfold allows you to organize inline forms into tab navigation by setting the `tab` attribute to `True` in your inline class definition. This feature is specifically designed for changeform pages, providing a cleaner and more organized interface when dealing with multiple inline forms. Each inline class you set `tab` to `True` will be displayed in its own tab.

Additionally, it's possible to display more than one inline in a single tab, by setting a common `tab_group` attribute in the definitions of the inline classes to be grouped. This attribute value should be the string value meant to be the tab label. When including multiple inline classes on a single tab, the `show_count` attribute is ignored.

Please note that without implementing custom code, it is not possible to add other types of custom tabs to this navigation system. The tab navigation for inlines works independently from the main tab system and is specifically tailored for managing related model instances.

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

class GroupedTabularInline(TabularInline):
    model = RelatedModel
    tab = True
    tab_group = "Grouped tabs"

class GroupedStackedInline(StackedInline):
    model = OtherRelatedModel
    tab = True
    tab_group = "Grouped tabs"
```
