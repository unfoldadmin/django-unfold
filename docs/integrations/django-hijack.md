---
title: django-hijack
order: 0
description: Integration guide for django-hijack with Unfold admin to enable seamless user switching and improved notification styling.
---

# django-hijack

Follow the official installation instructions for `django-hijack`. Once it is installed, add `unfold.contrib.hijack` to your `INSTALLED_APPS` in `settings.py`.

This integration enhances the styling of notifications indicating the currently impersonated user, as well as the buttons on the user changelist page.

```python
# settings.py

INSTALLED_APPS = [
    "unfold.contrib.hijack", # Add this to load new templates
]
```

**LIMITATION**: Once you leave the admin area, the notification may not display correctly because the admin styles are no longer applied.