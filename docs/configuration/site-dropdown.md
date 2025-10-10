---
title: Site dropdown
order: 2
description: Learn how to configure dropdown navigation in the sidebar when clicking on the site header in Django Unfold admin interface.
---

# Site dropdown

Django Unfold offers a flexible way to enhance your admin interface by adding a dropdown navigation menu in the sidebar. This feature is activated when clicking on the site header and can be configured using the `SITE_DROPDOWN` option within the `UNFOLD` configuration dictionary. When you enable this feature by setting the option, a dropdown icon will automatically appear next to the site header, providing a visual indication that it's interactive and can be clicked to reveal additional navigation options.

[![Unfold site dropdown](/static/docs/configuration/unfold-site-dropdown.webp)](/static/docs/configuration/unfold-site-dropdown.webp)

You can explore this feature in action by visiting our live demo at https://demo.unfoldadmin.com. Simply navigate to the top left corner of the interface and click on the site title - you'll see the dropdown menu elegantly appear, showcasing the navigation options. This interactive demo provides a hands-on way to understand how the dropdown navigation enhances the admin interface's usability.

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
            "attrs": {
                "target": "_blank",
            },
        },
        {
            "icon": "diamond",
            "title": _("My site"),
            "link": reverse_lazy("admin:index"),
        },
    ]
}
```
