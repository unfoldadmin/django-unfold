---
title: Changeform actions
description: Implement and customize object-specific actions in Django Unfold's admin detail view, featuring permission handling, dropdown menus, and custom action callbacks for efficient object management.
order: 3
---

# Changeform actions

Changeform actions appear as buttons at the top of the detail/change form page for individual objects. These actions provide quick access to object-specific operations directly from the detail view. Unlike changelist actions, changeform actions receive the `object_id` parameter, allowing you to perform operations on the specific object being viewed.

[![Changeform actions](/static/docs/actions/changeform-actions.webp)](/static/docs/actions/changeform-actions.webp)

When implementing permissions for changeform actions, you can use the `has_[action_name]_permission` method which receives both the `request` and `object_id` parameters. This allows you to implement object-specific permission logic that can vary based on the individual object's properties or state.

The actions are defined using the `actions_detail` attribute in your ModelAdmin class. Each action can be customized with various parameters like description, URL path, HTML attributes, and permission requirements using the `@action` decorator.

You can also organize multiple changeform actions into dropdown menus for a cleaner interface, similar to changelist actions. The dropdown functionality allows you to group related actions together under a single menu button.


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
    actions_detail = ["changeform_action"]

    @action(
        description=_("Changeform action"),
        url_path="changeform-action",
        attrs={"target": "_blank"},
        permissions=["changeform_action"]
    )
    def changeform_action(self, request: HttpRequest, object_id: int):
        user = User.objects.get(pk=object_id)
        user.block()

        return redirect(
            reverse_lazy("admin:users_user_change", args=(object_id,))
        )


    def has_changeform_action_permission(self, request: HttpRequest, object_id: Union[str, int]):
        pass
```
