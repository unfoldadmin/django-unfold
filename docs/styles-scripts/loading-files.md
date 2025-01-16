---
title: Loading styles and scripts
order: 0
description: Settings.py configuration for loading custom styles and scripts files in Unfold.
---

# Loading styles and scripts

To add custom styles, for example for a custom dashboard, you can load them via the **STYLES** key in the **UNFOLD** dictionary in settings.py. This key accepts a list of strings or lambda functions that will be loaded on all pages. JavaScript files can be loaded using a similar approach with the **SCRIPTS** key.

```python
# settings.py

from django.templatetags.static import static

UNFOLD = {
    "STYLES": [
        lambda request: static("css/styles.css"),
    ],
    "SCRIPTS": [
        lambda request: static("js/scripts.js"),
    ],
}
```

**Note:** When deploying to production, make sure to run the `python manage.py collectstatic` command to collect all static files. This ensures that all custom styles and scripts are properly included in the production build.
