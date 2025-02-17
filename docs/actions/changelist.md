---
title: Changelist actions
description: Changelist actions for list view.
order: 1
---

# Changelist actions

These actions will appear at the top of the changelist page as buttons. Please not that these actions are not displayed in the actions dropdown which is provided by default in Django. Changelist action will not reciver any queryset or object ids, because it is meant to be used for general actions for given model.

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
