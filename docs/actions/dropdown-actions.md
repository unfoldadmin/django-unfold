---
title: Dropdown action
description: Learn how to organize multiple admin actions into clean dropdown menus in Django Unfold, with support for icons and grouping
order: 6
---

# Dropdown actions

Django Unfold provides built-in support for organizing actions into dropdown menus, offering a clean and efficient way to handle multiple actions in your admin interface. This feature is particularly valuable when you need to manage numerous actions while maintaining a tidy and organized user interface. The dropdown functionality is available out of the box for both `actions_list` and `actions_detail` actions, allowing you to group related actions together in an intuitive menu structure. However, please note that this dropdown functionality is not currently supported for `actions_submit_line` and `actions_row` actions.

[![Dropdown actions](/static/docs/actions/dropdown-actions.webp)](/static/docs/actions/dropdown-actions.webp)

To implement a dropdown menu, you'll need to provide a dictionary containing two required keys: `title` and `items`. The `title` key defines the text that will appear as the dropdown button label, while the `items` key accepts a list of action names that will be displayed as menu options when the dropdown is expanded. For additional customization, you can include an optional `icon` key to display an icon alongside the dropdown title, enhancing the visual appeal and usability of your interface.

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
