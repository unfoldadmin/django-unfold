---
title: Changelist tabs
order: 1
description: Learn how to configure and customize tab navigation in Django Unfold admin changelist views, including model-specific tabs and permission-based access control.
---

# Changelist tabs

Django Unfold provides powerful tab navigation capabilities for changelist views, allowing you to create an organized and intuitive interface. You can enhance your admin interface by adding multiple tabs that can link to various registered admin models or custom views. The tab navigation system is highly configurable and can be customized to match your specific administrative needs. All configuration settings are managed through the `UNFOLD` dictionary under `TABS` key in your project's `settings.py` file, making it easy to maintain and update your tab structure as your application evolves.

[![Changelist Tabs](/static/docs/tabs/changelist-tabs.webp)](/static/docs/tabs/changelist-tabs.webp)

```python
# settings.py

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "TABS": [
        {
            # Which models are going to display tab navigation
            "models": [
                "app_label.model_name_in_lowercase",
            ],
            # List of tab items
            "items": [
                {
                    "title": _("Your custom title"),
                    "link": reverse_lazy("admin:app_label_model_name_changelist"),
                    "permission": "sample_app.permission_callback",
                },
                {
                    "title": _("Another custom title"),
                    "link": reverse_lazy("admin:app_label_another_model_name_changelist"),
                    "permission": "sample_app.permission_callback",
                },
            ],
        },
    ],
}

# Permission callback for tab item
def permission_callback(request):
    return request.user.has_perm("sample_app.change_model")
```
