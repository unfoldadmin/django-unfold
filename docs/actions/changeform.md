---
title: Changeform actions
description: Changeform actions for detail view.
order: 3
---

# Changeform actions

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
