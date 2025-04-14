---
title: Component - Button
order: 5
description: Comprehensive guide to Django Unfold's Button component, featuring examples of implementation in templates, customization options, styling variants, and support for both button and link functionality with full dark mode compatibility.
---

# Button component

The Button component provides a standardized way to display interactive buttons in the Unfold interface. It can function as either a button or a link (with href), and supports primary and default styling variants. The component features consistent spacing, typography, and visual feedback states, with full dark mode support for optimal readability in both light and dark environments.

## Button component in HTML template

The Button component can be easily implemented in your Django templates. It supports both standard buttons and link-style buttons, with customizable styling and content. Below is an example of how to use the button component in a Django HTML template:

```html
{% load i18n unfold %}

{% url "admin:index" as dashboard_link %}
{% trans "Button title" as button_title %}

{% component "unfold/components/button.html" with href=dashboard_link %}
    {{ button_title }}
{% endcomponent %}
```

## Providing custom attrs to button component

The Button component supports custom HTML attributes through the `attrs` parameter. This allows you to add any standard HTML button attributes like `disabled`, `form`, `data-*` attributes, and more.

```python
def dashboard_callback(request):
    return {
        "button": {
            "title": "Button title",
            "attrs":
                "disabled": "disabled",
                "form": "form-id",
            },
        },
    }
```

To apply custom attributes to a button component, pass the `attrs` parameter with your attribute dictionary:

```
{% load unfold %}

{% component "unfold/components/button.html" with attrs=button.attrs %}
    {{ button.title }}
{% endcomponent %}
```

## Button component parameters

| Parameter                         | Description                                            |
| --------------------------------- | ------------------------------------------------------ |
| submit                            | Button will have a type="submit" attribute             |
| name                              | Adds a "name" attribute to the button                  |
| href                              | Displays the button as a link                          |
| variant                           | "default" value displays the button without any colors |
| attrs                             | Dictionary with a list of custom attributes            |
