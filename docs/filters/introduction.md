---
title: Introduction to filters
order: 0
description: Introduction to Unfold filters.
---

# Filters

By default, Django admin handles all filters as regular HTML links pointing at the same URL with different query parameters. This approach is for basic filtering more than enough. In the case of more advanced filtering by incorporating input fields, it is not going to work.

All custom filters implemented in Unfold are located in separate application `unfold.contrib.filters`. In order to use these filters, it is required to add this application into `INSTALLED_APPS` in `settings.py` right after `unfold` application.

```python
# settings.py

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
]
```

**Note:** when implementing a filter which contains input fields, there is a no way that user can submit the values, because default filters does not contain submit button. To implement submit button, `unfold.admin.ModelAdmin` contains boolean `list_filter_submit` flag which enables submit button in filter form.
