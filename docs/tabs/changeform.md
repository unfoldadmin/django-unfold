---
title: Changeform tabs
order: 2
description: Learn how to configure and customize tab navigation in Django Unfold admin changeform views, including model-specific tabs and permission-based access control.
---

# Changeform tabs

In changeform view, it is possible to add custom tab navigation. It can consist from various custom links which can point at another registered admin models. The configuration is done in `UNFOLD` dictionary in `settings.py`.

Actually, the changeform tab navigation configuration is the same as the changelist tab navigation configuration. The only difference is that in `models` section it is required to specify model name as dictionary with `detail` key set to `True`.

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
                    "app_label.model_name_in_lowercase",
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
