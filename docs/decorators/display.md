---
title: Display
description: Enhance Django admin display fields with Unfold's @display decorator, featuring label-based styling, header formatting, and advanced customization options for improved data presentation and visual organization.
order: 1
---

# Unfold @display decorator

Unfold provides its own enhanced version of the display decorator through `unfold.decorators.display`. While maintaining complete compatibility with Django's native `django.contrib.admin.decorators.display`, this decorator introduces additional customization options that extend the default functionality in powerful ways.

The decorator supports label-based display through two main approaches: `@display(label=True)` or `@display(label={"value1": "success"})`. This feature is particularly useful for displaying status indicators and other categorical information. When using `label=True`, the decorator will render the value with a default color scheme. Alternatively, you can pass a dictionary to customize the colors for different values. The supported color schemes include:
- success (green) - for positive or completed states
- info (blue) - for informational or neutral states
- warning (orange) - for cautionary states
- danger (red) - for critical or error states

For more complex display needs, `@display(header=True)` enables showing two distinct pieces of information within a single table cell in the results list. This is especially valuable when presenting related information together - for instance, showing a customer's name on the first line followed by their email address below. Methods using this decorator should return a tuple or list containing two elements, like `return "Full name", "E-mail address"`. Additionally, you can provide a third optional argument that displays a circular badge containing text (such as initials) before the two main values, creating a visually appealing and informative layout.

```python
# admin.py

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
from unfold.decorators import display


class UserStatus(TextChoices):
    ACTIVE = "ACTIVE", _("Active")
    PENDING = "PENDING", _("Pending")
    INACTIVE = "INACTIVE", _("Inactive")
    CANCELLED = "CANCELLED", _("Cancelled")


class UserAdmin(ModelAdmin):
    list_display = [
        "display_as_two_line_heading",
        "show_status",
        "show_status_with_custom_label",
    ]

    @display(
        description=_("Status"),
        ordering="status",
        label=True
    )
    def show_status_default_color(self, obj):
        return obj.status

    @display(
        description=_("Status"),
        ordering="status",
        label={
            UserStatus.ACTIVE: "success",  # green
            UserStatus.PENDING: "info",  # blue
            UserStatus.INACTIVE: "warning",  # orange
            UserStatus.CANCELLED: "danger",  # red
        },
    )
    def show_status_customized_color(self, obj):
        return obj.status

    @display(description=_("Status with label"), ordering="status", label=True)
    def show_status_with_custom_label(self, obj):
        return obj.status, obj.get_status_display()

    @display(header=True)
    def display_as_two_line_heading(self, obj):
        """
        Third argument is short text which will appear as prefix in circle
        """
        return [
            "First main heading",
            "Smaller additional description",  # Use None in case you don't need it
            "AB",  # Short text which will appear in front of
            # Image instead of initials. Initials are ignored if image is available
            {
                "path": "some/path/picture.jpg",
                "squared": True, # Picture is displayed in square format, if empty circle
                "borderless": True,  # Picture will be displayed without border
                "width": 64, # Removes default width. Use together with height
                "height": 48, # Removes default height. Use together with width
            }
        ]
```

## Dropdown support

In the changelist view, you can enhance any field by applying `dropdown=True` to create an interactive dropdown menu. When enabled, the field will be displayed as a clickable link that reveals a dropdown menu when clicked. Unfold provides two flexible approaches for rendering dropdown content:

- You can provide a list of `items` to generate a traditional dropdown menu. This approach is particularly useful when you need to display a collection of related objects or actions in an organized list format.
- Alternatively, you can use the `content` attribute to render custom HTML content within the dropdown. This gives you complete control over the dropdown's layout and styling, making it ideal for more complex UI requirements.

### Creating a list-based Dropdown

The following example illustrates how to implement a dropdown menu with a list of clickable items. The dropdown configuration supports several customization options:

- `title` (required) - The text that appears in the column header and serves as the dropdown trigger
- `items` (required) - An array of menu items to be displayed in the dropdown. Each item requires:
  - `title` - The text label for the menu item
  - `link` (optional) - A URL or path that the item will link to when clicked
- `striped` (optional) - When set to true, adds alternating background colors to list items for better visual separation
- `height` (optional) - Sets a maximum height in pixels, after which the content becomes scrollable
- `width` (optional) - Defines the dropdown's width in pixels for precise layout control

The dropdown menu automatically positions itself below the trigger element and includes built-in behavior to close when clicking outside the menu or selecting an item.


```python
class UserAdmin(ModelAdmin):
    list_display = [
        "display_dropdown",
    ]

    @display(description=_("Status"), dropdown=True)
    def display_dropdown(self, obj):
        return {
            # Clickable title displayed in the column
            "title": "Custom dropdown title",
            # Striped design for the items
            "striped": True,  # Optional
            # Dropdown height. Will display scrollbar for longer content
            "height": 200,  # Optional
            # Dropdown width
            "width": 240,  # Optional
            "items": [
                {
                    "title": "First title",
                    "link": "#"  # Optional
                },
                {
                    "title": "Second title",
                    "link": "#"  # Optional
                },
            ]
        }
```

### Custom dropdown template

For more advanced use cases, you can render a custom template within the dropdown menu. This is achieved by passing the `content` parameter containing your template content. For complex templates or dynamic content, it's recommended to use Django's `render_to_string` function to generate the HTML output.

When implementing a custom template dropdown, the configuration accepts the following parameters:

- `title` (required) - The text that appears in the column header and acts as the dropdown trigger button
- `content` (required) - The HTML content or template string that will be rendered inside the dropdown menu

The dropdown menu is automatically positioned directly beneath the trigger element and includes built-in functionality to close when users click outside of it. You have complete flexibility in terms of content - the dropdown can contain any valid HTML markup or Django template syntax, allowing you to create rich, interactive dropdown interfaces.

```python
class UserAdmin(ModelAdmin):
    list_display = [
        "display_dropdown",
    ]

    @display(description=_("Status"), dropdown=True)
    def display_dropdown(self, obj):
        return {
            "title": "Custom dropdown title",
            "content": "template content",
        }
```
