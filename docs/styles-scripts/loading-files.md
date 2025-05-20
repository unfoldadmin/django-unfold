---
title: Loading styles and scripts
order: 0
description: Configure and manage custom CSS and JavaScript files in Django Unfold admin interface through settings.py, with guidance on static file handling and deployment best practices.
---

# Loading styles and scripts

Custom styles, such as those needed for a custom dashboard, can be loaded by configuring the **STYLES** key within the **UNFOLD** dictionary in your settings.py file. This key accepts a list of either strings or lambda functions, and the specified files will be loaded across all pages. For JavaScript files, you can use the same approach by utilizing the **SCRIPTS** key.

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
