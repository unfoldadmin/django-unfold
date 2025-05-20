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

The example below demonstrates how to implement ArrayWidget in your Django admin class. By using the `formfield_overrides` setting, you can configure all `ArrayField` fields to utilize the `ArrayWidget` for rendering input fields. The widget provides flexibility in how the data is displayed - when `choices` are specified, it automatically switches from a standard text input to a dropdown list interface, allowing users to select from predefined options. This makes it particularly useful for managing array data that should be constrained to a specific set of values.

[![Array widget](/static/docs/widgets/array.webp)](/static/docs/widgets/array.webp)

When implementing the ArrayWidget with choices, it's important to note that the widget itself doesn't automatically inherit or detect any choice options from the field definition. This means you'll need to explicitly provide the choices when initializing the widget. The recommended approach is to override the `get_form` method in your ModelAdmin class, where you can initialize the widget with the desired `choices` parameter. This gives you full control over what options are available in the dropdown list and ensures that the widget properly constrains user input to valid selections. The choices can be defined using Django's TextChoices class or any other compatible choices format.

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
