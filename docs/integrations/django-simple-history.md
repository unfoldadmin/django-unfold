---
title: django-simple-history
order: 0
description: Learn how to integrate django-simple-history with Django Unfold admin panel to track and display model history changes for seamless version control and change tracking.
---

# django-simple-history

To integrate this application with your Django project, add `unfold.contrib.simple_history` to the `INSTALLED_APPS` variable in your `settings.py` file. It's important to place it after `unfold` but before `simple_history` in the list. This application ensures that all templates from django-simple-history are properly overridden by Unfold's styling and components, maintaining a consistent look and feel throughout your admin interface.

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

Below you can find an example of how to use Unfold with django-simple-history. The most important part is to inherit from both the `SimpleHistoryAdmin` and `unfold.admin.ModelAdmin` classes in your admin configuration. This inheritance ensures that you get both the history tracking functionality and Unfold's enhanced admin interface styling.

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

For comprehensive information about installation, configuration, and usage of django-simple-history, please refer to the [official documentation](https://django-simple-history.readthedocs.io/en/latest/). The documentation covers everything from basic setup to advanced features like tracking model changes, querying historical records, and customizing history tracking behavior.

[![Django Simple History](/static/docs/integrations/django-simple-history.webp)](/static/docs/integrations/django-simple-history.webp)

A live demo of the [django-simple-history integration with Unfold](https://demo.unfoldadmin.com/en/admin/formula/driver/56/history/) is available for you to explore. This demo showcases how Unfold seamlessly integrates with django-simple-history's history tracking interface, providing an enhanced user experience for viewing and managing model history.
