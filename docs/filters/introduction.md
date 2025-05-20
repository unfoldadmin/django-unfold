---
title: Introduction to filters
order: 0
description: Enhance Django's admin filtering capabilities with Unfold's custom filters. Discover advanced filtering features, input field filters, and proper configuration for seamless integration with your Django project.
---

# Filters

By default, Django's admin interface handles filtering through regular HTML links that modify URL query parameters. While this approach works well for basic filtering needs, it becomes limiting when dealing with more advanced filtering requirements, particularly when input fields are involved.

Unfold extends Django's filtering capabilities through its custom filters, which are contained in a dedicated application called `unfold.contrib.filters`. To utilize these enhanced filtering features in your project, you'll need to add this application to your `INSTALLED_APPS` configuration in `settings.py`. It's important to place it immediately after the main `unfold` application to ensure proper functionality.

```python
# settings.py

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
]
```

**Note:** When implementing filters with input fields, users need a way to submit their values since default filters don't include a submit button. To add a submit button to the filter form, set the `list_filter_submit` boolean flag to `True` in your `unfold.admin.ModelAdmin` class.
