---
title: django-simple-history
order: 0
description: Learn how to integrate django-simple-history with Django Unfold admin panel to track and display model history changes for seamless version control and change tracking.
---

# django-simple-history

To make this application work, add `unfold.contrib.simple_history` to the `INSTALLED_APPS` variable in `settings.py`, placing it after `unfold` but before `simple_history`. This app ensures that templates from django-simple-history are overridden by Unfold.

```python
# settings.py

INSTALLED_APPS = [
    "unfold",
    # ...
    "unfold.contrib.simple_history",
    # ...
    "simple_history",
]
```

Below you can find an example of how to use Unfold with django-simple-history. The important part is to inherit from `SimpleHistoryAdmin` and `unfold.adminModelAdmin`.

```python
# admin.py

from django.contrib import admin
from django.contrib.auth import get_user_model

from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(SimpleHistoryAdmin, ModelAdmin):
    pass
```
