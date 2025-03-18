---
title: Conditional fields
order: 3
description: Learn how to implement dynamic forms with conditional fields in Django Unfold admin interface. Control field visibility based on other field values using Alpine.js expressions for a more intuitive user experience.
---

# Conditional fields

Django Unfold offers a powerful feature for creating dynamic forms through conditional fields. This functionality allows you to control the visibility of specific form fields based on the values of other fields in your form. By implementing conditional logic, you can create more intuitive and streamlined user interfaces that only display relevant fields when they're needed.

With conditional fields, you can:

- Show or hide fields based on the state of other form inputs
- Create cleaner, less cluttered forms by revealing fields only when necessary
- Improve the user experience by presenting a more focused interface

The conditional display is powered by Alpine.js expressions, giving you flexibility in defining when fields should appear.

```python
# models.py

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    different_address = models.BooleanField(_("different address"), default=False)
    country = models.CharField(_("city"), max_length=255, null=True, blank=True, default=None)
    city = models.CharField(_("city"), max_length=255, null=True, blank=True, default=None)
    address = models.CharField(_("address"), max_length=255, null=True, blank=True, default=None)

    class Meta:
        db_table = "users"
        verbose_name = _("user")
        verbose_name_plural = _("users")
```

## Implementing Conditional Fields

Using the model defined above, we can implement conditional field display by configuring the `conditional_fields` dictionary in our ModelAdmin class. This powerful feature allows for dynamic form behavior based on user input.

The `conditional_fields` dictionary uses a straightforward key-value structure:
- Each **key** corresponds to a field name from your model that you want to conditionally display
- Each **value** contains JavaScript/Alpine.js expression that evaluates to either true or false, determining whether the field should be visible

When a user interacts with your form, Django Unfold evaluates these expressions in real-time, showing or hiding fields accordingly. This creates a responsive, interactive experience without requiring page reloads.

For fields that use multiple widgets (like SplitDateTimeField), Django Unfold automatically handles the complexity by assigning numeric suffixes to each widget component. For example, a date-time field named `date_start` would have its widgets accessible as `date_start_0` and `date_start_1` in your conditional expressions.

This approach is particularly useful for complex forms where certain information is only relevant based on specific user choices, helping to reduce visual clutter and guide users through your interface more effectively.

```python
# admin.py

from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import User


@admin.register(User)
class UserAdmin(ModelAdmin):
    conditional_fields = {
        "country": "different_address == true"
        "city": "different_address == true"
        "address": "different_address == true"
    }
```
