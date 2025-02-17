---
title: Changelist row actions
description: Customize and add row-level actions to your Django admin changelist view with Unfold's powerful action system.
order: 2
---

# Changelist row actions

These actions will appear on seach row on the changelist page as a dropdown button containing all custom row actions. The permission callback for `actions_row` does not accept `object_id` as an argument. Actions can have permission set globally and it is not possible to control permission per row.

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
