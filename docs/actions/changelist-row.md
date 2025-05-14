---
title: Changelist row actions
description: Learn how to implement row-level actions in Django Unfold's admin interface, including dropdown menus, permission handling, and custom action callbacks for efficient object-specific operations.
order: 2
---

# Changelist row actions

Row actions appear on each individual row in the changelist page as a dropdown button that contains all custom actions defined for that row. These actions provide quick access to row-specific operations directly from the list view. When implementing permissions for row actions, note that the permission callback for `actions_row` does not accept an `object_id` parameter. This means that permissions can only be set globally for all rows - it is not possible to implement row-specific permission logic that varies based on the individual object being acted upon.

[![Changelist row actions](/static/docs/actions/changelist-row-actions.webp)](/static/docs/actions/changelist-row-actions.webp)

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
    actions_row = ["changelist_row_action"]

    @action(
        description=_("Changelist row action"),
        permissions=["changelist_row_action"],
        url_path="changelist-row-action",
        attrs={"target": "_blank"}
    )
    def changelist_row_action(self, request: HttpRequest, object_id: int):
        return redirect(
          reverse_lazy("admin:users_user_changelist")
        )

    def has_changelist_row_action_permission(self, request: HttpRequest):
        # Write your own bussiness logic. Code below will always display an action.
        return True
```
