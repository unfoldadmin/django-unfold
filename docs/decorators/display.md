---
title: Display
description: Custom Unfold @display decorator.
order: 1
---

# Unfold @display decorator

Unfold introduces it's own `unfold.decorators.display` decorator. By default it has exactly same behavior as native `django.contrib.admin.decorators.display` but it adds same customizations which helps to extends default logic.

`@display(label=True)`, `@display(label={"value1": "success"})` displays a result as a label. This option fits for different types of statuses. Label can be either boolean indicating we want to use label with default color or dict where the dict is responsible for displaying labels in different colors. At the moment these color combinations are supported: success(green), info(blue), danger(red) and warning(orange).

`@display(header=True)` displays in results list two information in one table cell. Good example is when we want to display customer information, first line is going to be customer's name and right below the name display corresponding email address. Method with such a decorator is supposed to return a list with two elements `return "Full name", "E-mail address"`. There is a third optional argument, which is type of the string and its value is displayed in a circle before first two values on the front end. Its optimal usage is for displaying initials.

```python
# admin.py

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
from unfold.decorators import display


class UserStatus(TextChoices):
    ACTIVE = "ACTIVE", _("Active")
    PENDING = "PENDING", _("Pending")
    INACTIVE = "INACTIVE", _("Inactive")
    CANCELLED = "CANCELLED", _("Cancelled")


class UserAdmin(ModelAdmin):
    list_display = [
        "display_as_two_line_heading",
        "show_status",
        "show_status_with_custom_label",
    ]

    @display(
        description=_("Status"),
        ordering="status",
        label=True
    )
    def show_status_default_color(self, obj):
        return obj.status

    @display(
        description=_("Status"),
        ordering="status",
        label={
            UserStatus.ACTIVE: "success",  # green
            UserStatus.PENDING: "info",  # blue
            UserStatus.INACTIVE: "warning",  # orange
            UserStatus.CANCELLED: "danger",  # red
        },
    )
    def show_status_customized_color(self, obj):
        return obj.status

    @display(description=_("Status with label"), ordering="status", label=True)
    def show_status_with_custom_label(self, obj):
        return obj.status, obj.get_status_display()

    @display(header=True)
    def display_as_two_line_heading(self, obj):
        """
        Third argument is short text which will appear as prefix in circle
        """
        return [
            "First main heading",
            "Smaller additional description",  # Use None in case you don't need it
            "AB",  # Short text which will appear in front of
            # Image instead of initials. Initials are ignored if image is available
            {
                "path": "some/path/picture.jpg",
                "squared": True, # Picture is displayed in square format, if empty circle
                "borderless": True,  # Picture will be displayed without border
                "width": 64, # Removes default width. Use together with height
                "height": 48, # Removes default height. Use together with width
            }
        ]
```
