---
title: Dynamic tabs
order: 6
description: Learn how to dynamically generate tab navigation in Django Unfold admin using custom callbacks and render tabs in custom templates.
---

# Dynamic tabs

Unfold provides a way to dynamically generate tab navigation. It is possible to use your own logic to generate tab navigation. The tab navigation configuration can be defined as importable string which will call a function with `HttpRequest` object as an argument. In this function it is possible to build own tabs navigation structure.

```python
# settings.py

UNFOLD = {
    "TABS": "your_project.admin.tabs_callback"
}
```

Below is an example of how to build own tabs navigation structure in tabs callback function. Based on the request object it is possible to write own logic for the tab navigation structure.

```python
# admin.py

from django.http import HttpRequest


def tabs_callback(request: HttpRequest) -> list[dict[str, Any]]:
    return [
        {
            # Unique tab identifier to render tabs in custom templates
            "page": "custom_page",

            # Applies for the changeform view
            "models": [
                {
                    "name": "app_label.model_name_in_lowercase",
                    "detail": True
                },
            ],
            "items": [
                {
                    "title": _("Your custom title"),
                    "link": reverse_lazy("admin:app_label_model_name_changelist"),
                    "is_active": True # Configure active tab
                },
            ],
        },
    ],
```

## Rendering tabs in custom templates

Unfold provides a `tab_list` template tag which can be used to render tabs in custom templates. The only required argument is the `page` name which is defined in `TABS` structure on particular tab navigation. Configure `page` key to something unique and then use `tab_list` template tag in your custom template where the first parameter is the unique `page` name.

```python
# settings.py

from django.http import HttpRequest

UNFOLD = {
    "TABS": [
        {
            "page": "custom_page", # Unique tab identifier
            "items": [
                {
                    "title": _("Your custom title"),
                    "link": reverse_lazy("admin:app_label_model_name_changelist"),
                },
            ],
        }
    ]
}
```

Below is an example of how to render tabs in custom templates. It is important to load `unfold` template tags before using `tab_list` template tag.

```html
{% extends "admin/base_site.html" %}

{% load unfold %}

{% block content %}
    {% tab_list "custom_page" %}
{% endblock %}
```

**Note:** When it comes which tab item is active on custom page, it is not up to Unfold to find out a way how to mark links as active. The tab configuration provides `is_active` key which you can use to set active tab item.
