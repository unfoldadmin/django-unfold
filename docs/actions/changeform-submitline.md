---
title: Changeform submitline actions
description: Changeform submitline actions for detail view.
order: 4
---

# Changeform submitline actions

Submit row actions work a bit differently when compared to other custom Unfold actions. These actions first invoke form save (same as if you hit `Save` button) and then lets you perform additional logic on already saved instance.

```python
# admin.py

from django.contrib.admin import register
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest
from unfold.admin import ModelAdmin
from unfold.decorators import action


@register(User)
class UserAdmin(ModelAdmin):
    actions_submit_line = ["changeform_submitline_action"]

    @action(
        description=_("Changeform submitline action"),
        permissions=["changeform_submitline_action"]
    )
    def changeform_submitline_action(self, request: HttpRequest, obj: User):
        """
        If instance is modified in any way, it also needs to be saved, since this handler is invoked after instance is saved.
        """

        obj.is_active = True
        obj.save()

    def has_changeform_submitline_action_permission(self, request: HttpRequest, object_id: Union[str, int]):
        # Write your own bussiness logic. Code below will always display an action.
        return True
```
