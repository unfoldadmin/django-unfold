---
title: Display
description: Custom Unfold @display decorator.
order: 1
---

# Unfold @display decorator

Unfold introduces its own `unfold.decorators.display` decorator. By default, it has exactly the same behavior as the native `django.contrib.admin.decorators.display` but it adds customizations which help to extend the default logic.

`@display(label=True)`, `@display(label={"value1": "success"})` displays a result as a label. This option fits for different types of statuses. The label can be either a boolean indicating we want to use a label with the default color, or a dict where the dict is responsible for displaying labels in different colors. At the moment these color combinations are supported: success (green), info (blue), danger (red) and warning (orange).

`@display(header=True)` displays two pieces of information in one table cell in the results list. A good example is when we want to display customer information - the first line will be the customer's name and right below the name, the corresponding email address is displayed. A method with such a decorator is supposed to return a list with two elements `return "Full name", "E-mail address"`. There is a third optional argument, which is the type of string and its value is displayed in a circle before the first two values on the front end. Its optimal usage is for displaying initials.

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

For the changelist, it is possible to apply `dropdown=True` which will display a clickable link. After clicking on the link, a dropdown will appear. There are two supported options for rendering the content of the dropdown:

- Providing a list of `items`. This will render a classic list of items, which is a good option for displaying a list of related objects.
- Defining the `content` attribute which will display your custom content in the dropdown. This is handy for rendering complex layouts in the dropdown.

### Rendering list of options

The following example demonstrates how to create a dropdown with a list of items. The dropdown configuration accepts these options:

- `title` (required) - The text displayed in the column that users click to open the dropdown
- `items` (required) - List of items to display in the dropdown menu. Each item should have:
  - `title` - Text to display for the item
  - `link` (optional) - URL the item links to
- `striped` (optional) - Boolean to enable alternating background colors for items
- `height` (optional) - Maximum height in pixels before scrolling is enabled
- `width` (optional) - Width of the dropdown in pixels

The dropdown will be positioned below the clicked element and will close when clicking outside or selecting an item.


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

You can also render a custom template inside a dropdown. Just pass the `content` parameter with template content. If you want to render more complex content, use `render_to_string`.

The dropdown configuration accepts these options when using custom template content:

- `title` (required) - The text displayed in the column that users click to open the dropdown
- `content` (required) - HTML content or template string to display in the dropdown

The dropdown will be positioned below the clicked element and will close when clicking outside. The content can include any valid HTML or Django template syntax.

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
