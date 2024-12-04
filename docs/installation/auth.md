---
title: User & group models
order: 2
description: User & group models configuration
---

# User & group models

By default, when `django.contrib.auth` is in `INSTALLED_APPS`, you are going to have user and group models in admin. Both models are going to work but they will look unstyled because they are not inheriting from `unfold.admin.ModelAdmin`.

The solution is to unregister default admin classes and then register them back by using `unfold.admin.ModelAdmin` like in the example below

```python
# admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group

from unfold.admin import ModelAdmin


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
```
