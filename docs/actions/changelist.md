---
title: Changelist actions
description: Implement and customize changelist actions in Django Unfold admin interface, featuring standalone action buttons, permissions handling, and model-wide operations for efficient data management.
order: 1
---

# Changelist actions

Changelist actions appear as buttons at the top of the changelist page, providing quick access to model-wide operations. Unlike standard Django actions that appear in the default actions dropdown, these actions are displayed as standalone buttons. It's important to note that changelist actions do not receive a queryset or object IDs as parameters, as they are designed for performing general operations on the model level rather than on specific selected objects. This makes them ideal for tasks like bulk imports, exports, or other model-wide administrative functions.

[![Changelist actions](/static/docs/actions/changelist-actions.webp)](/static/docs/actions/changelist-actions.webp)

```python
# admin.py

from django.contrib.admin import register
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest
from unfold.admin import ModelAdmin
from unfold.decorators import action


@register(User)
class UserAdmin(ModelAdmin):
    actions_list = ["changelist_action"]

    @action(description=_("Changelist action"), url_path="changelist-action", permissions=["changelist_action"])
    def changelist_action(self, request: HttpRequest):
        return redirect(
          reverse_lazy("admin:users_user_changelist")
        )

    def has_changelist_action_permission(self, request: HttpRequest):
        # Write your own bussiness logic. Code below will always display an action.
        return True
```
