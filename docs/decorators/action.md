---
title: Action
description: Customize Django admin actions using Unfold's enhanced @action decorator with URL paths, HTML attributes, icons, button variants, and permission checks for improved interface functionality.
order: 2
---

# Unfold @action decorator

Unfold extends Django's built-in `@action` decorator by providing its own enhanced version. This custom decorator maintains all the functionality of Django's base decorator while introducing several additional parameters that enable more customization and control over how actions are displayed and behave in the admin interface:

- `url_path`: Specifies a custom URL path name for the action. If not provided, Unfold will automatically generate an appropriate URL path. This allows you to override the default routing behavior.

- `attrs`: A dictionary of additional HTML attributes that will be added to the action's `<a>` element. For example, you can use `{"target": "_blank"}` to make the action open in a new browser tab.

- `description`: Allows you to set a custom title/description for the action that will be displayed in the admin interface. This helps make the action's purpose clearer to users.

- `icon`: Lets you specify a custom Material Symbols icon that will be displayed alongside the action button. This provides visual context for the action's functionality.

- `variant`: Determines the color style and appearance of the action button. This helps visually distinguish different types of actions.

- `permissions`: Defines permission checks that will be performed before allowing access to the action. For example, specifying "check_something" will cause Unfold to call the `has_check_something_permission` method to verify the user has appropriate permissions.

These are available action variants that can be used to style action buttons:

- `DEFAULT`: The standard button style, suitable for most common actions
- `PRIMARY`: Used for primary or main actions that you want to emphasize
- `SUCCESS`: Green-colored variant for successful or confirming actions like approving items
- `INFO`: Blue-colored variant for informational actions like viewing details
- `WARNING`: Yellow/orange variant for actions that require caution
- `DANGER`: Red-colored variant for destructive or irreversible actions like deletion

When defining an action, you can specify its visual style using the `variant` parameter. The following enum defines all available variant options:

```python
# unfold/enums.py

class ActionVariant(Enum):
    DEFAULT = "default"
    PRIMARY = "primary"
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    DANGER = "danger"
```
