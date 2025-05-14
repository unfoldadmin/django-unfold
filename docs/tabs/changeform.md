---
title: Changeform tabs
order: 2
description: Learn how to configure and customize tab navigation in Django Unfold admin changeform views, including model-specific tabs and permission-based access control.
---

# Changeform tabs

Django Unfold provides the ability to enhance your changeform views with custom tab navigation. This powerful feature allows you to create an organized and intuitive interface by adding multiple tabs that can link to various registered admin models or custom views. The tab navigation system is highly configurable and can be customized to match your specific administrative needs. All configuration settings are managed through the `UNFOLD` dictionary under `TABS` key in your project's `settings.py` file, making it easy to maintain and update your tab structure as your application evolves.

[![Changeform Tabs](/static/docs/tabs/changeform-tabs.webp)](/static/docs/tabs/changeform-tabs.webp)

The changeform tab navigation uses the same configuration structure as changelist tabs, with one key difference: in the `models` section, each model must be specified as a dictionary with `detail` set to `True` to enable tabs on the changeform view.

```python
# settings.py

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "TABS": [
        {
            # Which changeform models are going to display tab navigation
            "models": [
                {
                    "name": "app_label.model_name_in_lowercase",
                    "detail": True, # Displays tab navigation on changeform page
                },
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
