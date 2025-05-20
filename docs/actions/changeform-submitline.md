---
title: Changeform submitline actions
description: Implement and customize submit line actions in Django Unfold's admin detail view, featuring automatic form saving, permission handling, and object-specific operations for streamlined data management.
order: 4
---

# Changeform submitline actions

[![Changeform submitline actions](/static/docs/actions/changeform-submitline-actions.webp)](/static/docs/actions/changeform-submitline-actions.webp)

Changeform submitline actions operate differently from other custom actions in Unfold. When triggered, these actions first save the form data (equivalent to clicking the 'Save' button) before executing any additional logic. This means that by the time your custom action code runs, you'll be working with an already saved instance of the model. This workflow ensures data consistency by guaranteeing that all form changes are properly saved before any custom operations are performed.

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
