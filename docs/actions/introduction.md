---
title: Introduction to actions
order: 0
description: Run custom admin actions from different places.
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
from unfold.decorators import action  # Import @action decorator from Unfold

@admin.register(User)
class UserAdmin(ModelAdmin):
    actions_list = ["custom_action"]

    @action(description="Custom action")
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
