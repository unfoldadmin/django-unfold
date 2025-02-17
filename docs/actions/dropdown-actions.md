---
title: Dropdown action
description: Learn how to organize multiple admin actions into clean dropdown menus in Django Unfold, with support for icons and grouping
order: 6
---

# Dropdown actions

Unfold supports displaying actions in dropdown menu. This is useful when you have a lot of actions to display and you want to keep the UI clean so you can group them in dropdown. Unfold supports this functionality of the box for `actions_list` and `actions_detail` actions. Remaining actions for `actions_submit_line` and `actions_row` are not supported.

The dropdown menu is defined by providing a `dict` with `title` and `items` keys. `items` key is a list of actions that will be displayed in the dropdown menu. Optionally you can provide `icon` key to set the icon for the dropdown.

```python
# admin.py

from django.contrib.auth.models import User
from unfold.admin import ModelAdmin


@register(User)
class UserAdmin(ModelAdmin):
    actions_list = ["action1", "action2", {
        "title": "Dropdown action",
        "icon": "person",  # Optional, will display icon in the dropdown title
        "items": [
            "action3", "action4",
        ]
    }]
```

**Note:** If there are not actions to display in the dropdown, the action button will be not displayed at all.
