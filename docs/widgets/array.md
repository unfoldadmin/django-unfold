---
title: ArrayWidget
order: 1
description: Learn how to use Django Unfold's ArrayWidget to efficiently manage and display ArrayField data in your Django admin interface with support for both text inputs and dropdown lists.
---

# Unfold widget ArrayWidget

```python
# settings.py

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.forms",
]
```

Below you can see how to use ArrayWidget in your admin class. In this example, all `ArrayField` fields will use `ArrayWidget` to render input fields. If `choices` are provided for the widget, a dropdown list will be used instead of a text input.

When it comes to providing choices for the widget, by default the widget does not have any information about the field's choices, so it is mandatory to provide them manually. You can do this in the `get_form` method where the widget is initialized with the `choices` parameter.

```python
# admin.py

from django.contrib import admin
from django.contrib.postgres.fields import ArrayField
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import ArrayWidget


class SomeChoices(TextChoices):
    OPTION_1 = "OPTION_1", _("Option 1")
    OPTION_2 = "OPTION_2", _("Option 2")


@admin.register(MyModel)
class CustomAdminClass(ModelAdmin):
    formfield_overrides = {
        ArrayField: {
            "widget": ArrayWidget,
        }
    }

    # If you need to provide choices for the widget, you can do it in the get_form method.
    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields["array_field"].widget = ArrayWidget(choices=SomeChoices)
        return form
```
