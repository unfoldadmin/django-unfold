---
title: Introduction to actions
order: 0
description: Create and customize powerful Django admin actions with Unfold, featuring icon support and color variants for enhanced user experience.
---

# Actions

It is highly recommended to read the base [Django actions documentation](https://docs.djangoproject.com/en/5.1/ref/contrib/admin/actions/) before reading this section, since Unfold actions are derived from Django actions.

```python
# admin.py

from django.auth.models import User
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from unfold.admin import ModelAdmin
from unfold.decorators import action

@admin.register(User)
class UserAdmin(ModelAdmin):
    actions_list = ["custom_action"]

    @action(description="Custom action", icon="person")
    def custom_action(self, request: HttpRequest, queryset: QuerySet):
        pass
```

## Permissions

Unfold provides two distinct ways to handle permissions for actions:

1. **ModelAdmin Method-based Permissions**
   - Define a permission check method in your ModelAdmin class
   - The method name should follow the pattern `has_{permission_name}_permission`
   - This method receives the request and can optionally receive the object instance
   - Example: `has_custom_action_permission` for a permission named "custom_action"

2. **Django Built-in Permissions**
   - Use Django's permission system with the format `app_label.permission_codename`
   - These are standard Django permissions defined in your models
   - **Note:** When using built-in permissions (containing a dot in the string), the permission check will not receive the object instance during detail view checks

```python
from django.contrib import admin
from django.contrib.auth.models import User

from unfold.admin import ModelAdmin
from unfold.decorators import action


@admin.register(User)
class UserAdmin(ModelAdmin):
    @action(
        description="Custom action",
        permissions=["custom_action", "auth.view_user"]  # Using both permission types
    )
    def custom_action(self, request, queryset):
        pass

    def has_custom_action_permission(self, request, obj=None):
        # Custom permission logic here
        return request.user.is_superuser
```

## Icon support

Unfold supports custom icons for actions. Icons are supported for all actions types. You can set the icon for an action by providing `icon` parameter to the `@action` decorator.

```python
# admin.py

from django.db.models import QuerySet
from django.http import HttpRequest

from unfold.decorators import action

@action(description="Custom action", icon="person")
def custom_action(self, request: HttpRequest, queryset: QuerySet):
    pass
```

## Action variants

In Unfold it is possible to change a color of the action. Unfold supports different variants of actions. You can set the variant for an action by providing `variant` parameter to the `@action` decorator.

```python
# admin.py

from django.db.models import QuerySet
from django.http import HttpRequest

from unfold.decorators import action
# Import ActionVariant enum from Unfold to set action variant
from unfold.enums import ActionVariant

# class ActionVariant(Enum):
#     DEFAULT = "default"
#     PRIMARY = "primary"
#     SUCCESS = "success"
#     INFO = "info"
#     WARNING = "warning"
#     DANGER = "danger"

@action(description="Custom action", variant=ActionVariant.PRIMARY)
def custom_action(self, request: HttpRequest, queryset: QuerySet):
    pass
```

## Actions overview

Besides traditional actions selected from dropdown, Unfold supports several other types of actions. Following table gives overview of all available actions together with their recommended usage:

| Type           | Appearance                     | Usage                                                                 |
| -------------- | ------------------------------ | ----------------------------------------------------------------------|
| Global         | Changelist - top               | General actions for all instances in listing                          |
| Row            | Changelist - each row          | Action for one specific instance, executable from listing             |
| Detail         | Changeform - top               | Action for one specific instance, executable from detail              |
| Submit line    | Changeform - submit line       | Action performed during form submit (instance save)                   |

## For global, row and detail action

All these actions are based on custom URLs generated for each of them. Handler function for these views is basically function based view.

For actions without intermediate steps, you can write all the logic inside handler directly. Request and object ID are both passed to these action handler functions, so you are free to fetch the instance from database and perform any operations with it. In the end, it is recommended to return redirect back to either detail or listing based on where the action was triggered from.

For actions with intermediate steps, it is recommended to use handler function only to redirect to custom URL with custom view. This view can be extended from base Unfold view, to have unified experience.
