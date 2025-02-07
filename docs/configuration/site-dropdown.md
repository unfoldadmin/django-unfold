---
title: Site dropdown
order: 2
description: Learn how to configure dropdown navigation in the sidebar when clicking on the site header in Django Unfold admin interface.
---

# Site dropdown

Unfold provides a possibility to specify a dropdown navigation in sidebar when clicking on the site header by using `SITE_DROPDOWN` option in `UNFOLD` configuration dictionary. When this option is set, a dropdown icon will display on the site header to mark that site header is clickable.

```python
# settings.py

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


UNFOLD = {
    "SITE_DROPDOWN": [
        {
            "icon": "diamond",
            "title": _("My site"),
            "link": "https://example.com",
        },
        {
            "icon": "diamond",
            "title": _("My site"),
            "link": reverse_lazy("admin:index"),
        },
    ]
}
```
