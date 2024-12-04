---
title: Component - Tracker
order: 3
description: Tracker component in Unfold theme
---

# Tracker component

The tracker component is a visual representation of data points. It's useful for displaying activity or progress over time. Each cell in the tracker can be colored differently and can include a tooltip for additional information.

## Default tracker component implementation in template

You can use the default implementation of the tracker component in your template with the following code. Like the cohort component, you can either use a component class to prepare the data or pass the data directly.

Using component class:

```html
{% load unfold %}

{% component "unfold/components/tracker.html" with component_class="MyTrackerComponent" %}
{% endcomponent %}
```

Using data directly:

```html
{% load unfold %}

{% component "unfold/components/tracker.html" with data=my_data_variable %}
{% endcomponent %}
```

## Custom tracker data preparation in component class

Below you can see an example of a component class that prepares the data for the tracker component. The component in template will receive the `data` parameter that is passed to the `get_context_data` method.

```python
# admin.py

from unfold.components import BaseComponent

class MyTrackerComponent(BaseComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "data": DATA
        })
        return context
```

## Data structure example

```python
DATA = [
    {
        "color": "bg-primary-400 dark:bg-primary-700",
        "tooltip": "Custom value 1",
    },
    {
        "color": "bg-primary-400 dark:bg-primary-700",
        "tooltip": "Custom value 2",
    }
]
```
