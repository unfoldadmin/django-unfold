---
title: User & group models
order: 2
description: Configure and customize Django's built-in user and group models to work seamlessly with Unfold admin interface, including proper styling and form handling.
---

# User & group models

When `django.contrib.auth` is included in `INSTALLED_APPS`, Django automatically provides user and group models in the admin interface. While these models will function correctly, they will appear unstyled since they don't inherit from `unfold.admin.ModelAdmin`.

To resolve this, you need to unregister the default admin classes and re-register them using `unfold.admin.ModelAdmin` as shown in the example below. You'll also need to override the default user forms (from the `UserAdmin` class) that Django admin loads by default. The overridden forms will have the proper Unfold styling applied.

```python
# admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group

from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    # Forms loaded from `unfold.forms`
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
```
