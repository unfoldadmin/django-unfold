---
title: django-constance
order: 0
description: Integrate django-constance with Unfold admin interface to manage dynamic Django settings with a beautiful UI and enhanced form widgets
---

# django-constance

To get started, follow the installation instructions for django-constance from their official documentation at https://django-constance.readthedocs.io/en/latest/.

After installing django-constance, add `unfold.contrib.constance` to your `INSTALLED_APPS` setting. Make sure to place it before `constance` in the list to ensure the proper templates are loaded correctly.


```python
# admin.py

from django.contrib import admin
from constance.admin import Config, ConstanceAdmin


@admin.register(Config)
class ConstanceConfigAdmin(ConstanceAdmin):
    pass
```

Unfold comes with a pre-configured set of supported field types and their corresponding widgets. To use them, configure your `CONSTANCE_ADDITIONAL_FIELDS` setting as demonstrated in the example below. Additionally, `UNFOLD_CONSTANCE_ADDITIONAL_FIELDS` provides extra field types like `image_field` and `file_field` to enhance your form capabilities.

```python
# settings.py

from unfold.contrib.constance.settings import UNFOLD_CONSTANCE_ADDITIONAL_FIELDS


CONSTANCE_ADDITIONAL_FIELDS = {
    **UNFOLD_CONSTANCE_ADDITIONAL_FIELDS,

    # Example field configuration for select with choices. Not needed.
    "choice_field": [
        "django.forms.fields.ChoiceField",
        {
            "widget": "unfold.widgets.UnfoldAdminSelectWidget",
            "choices": (
                ("light-blue", "Light blue"),
                ("dark-blue", "Dark blue"),
            ),
        },
    ],
}
```
