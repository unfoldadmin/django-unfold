---
title: Developer Tools
order: 1
description: Learn how to configure and customize developer tools menu in Django Unfold admin interface, including external links to monitoring and development tools.
---

# Tools Configuration

In the admin interface, it is possible to add quick access links to various development and monitoring tools. The configuration is done in `UNFOLD` dictionary in `settings.py`. This feature provides a convenient way to access commonly used development tools directly from your admin interface.

## Basic Configuration

```python
# settings.py

from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "TOOLS_CONFIG": {
        "show_tools": True,
        "title": _("Developer Tools"),
        "tools": [
            {
                "name": _("Sentry"),
                "url": "https://sentry.io",
                "icon": "warning",
                "new_tab": True
            },
            {
                "name": _("RabbitMQ"),
                "url": "http://localhost:15672",
                "icon": "queue",
                "new_tab": True
            },
            {
                "name": _("Flower"),
                "url": "http://localhost:5555",
                "icon": "monitoring",
                "new_tab": True
            }
        ]
    }
}
```

## Configuration Options

### TOOLS_CONFIG Settings

The `TOOLS_CONFIG` dictionary accepts the following options:

- `show_tools` (boolean): Enable or disable the tools menu in the admin interface
- `title` (string): The title displayed at the top of the tools dropdown menu
- `tools` (list): A list of tool configurations

### Tool Configuration Options

Each tool in the `tools` list requires the following settings:

- `name` (string): The display name of the tool (supports translation)
- `url` (string): The URL where the tool can be accessed
- `icon` (string): Material Symbol icon name for the tool
- `new_tab` (boolean): Whether to open the link in a new tab

## Common Development Tools

Here are some typical development tools you might want to include:

```python
UNFOLD = {
    "TOOLS_CONFIG": {
        "show_tools": True,
        "title": _("Developer Tools"),
        "tools": [
            {
                "name": _("Error Tracking"),
                "url": "https://sentry.io",
                "icon": "warning",
                "new_tab": True
            },
            {
                "name": _("Message Queue"),
                "url": "http://localhost:15672",
                "icon": "queue",
                "new_tab": True
            },
            {
                "name": _("Task Monitor"),
                "url": "http://localhost:5555",
                "icon": "monitoring",
                "new_tab": True
            },
            {
                "name": _("System Logs"),
                "url": "/admin/logs",
                "icon": "description",
                "new_tab": True
            }
        ]
    }
}
```

## Material Icons

The tools menu uses Material Symbols for icons. Here are some commonly used icons for development tools:

- `warning` - For error tracking tools
- `description` - For logs and documentation
- `queue` - For message queues
- `monitoring` - For monitoring tools
- `settings` - For configuration tools
- `api` - For API documentation
- `code` - For development tools

You can find the complete list of available icons at [Material Symbols](https://fonts.google.com/icons).

## Interface

The tools menu appears in the admin header as an icon button. When clicked, it displays a dropdown menu with your configured tools. The menu:

- Automatically adapts to light/dark mode
- Uses your configured color scheme
- Provides clear visual feedback on hover
- Opens external links in new tabs when configured
