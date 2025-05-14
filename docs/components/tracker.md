---
title: Component - Tracker
order: 3
description: Implement and customize the Tracker component in Django Unfold with visual data representation, grid layouts, color customization, and tooltips for enhanced data visualization
---

# Tracker component

The tracker component provides a visual representation of data points in a grid-like format. It's particularly effective for displaying activity patterns, progress tracking, or data distribution over time periods. Each individual cell within the tracker can be customized with different colors to represent various states or values, and can be enhanced with tooltips to provide additional context or detailed information when users hover over them. This makes it an ideal choice for creating heatmaps, activity logs, or contribution graphs similar to those found in platforms like GitHub.

[![Cohort](/static/docs/components/tracker.webp)](/static/docs/components/tracker.webp)

## Default tracker component implementation in template

The tracker component can be easily integrated into your template using one of two approaches. Similar to the cohort component, you have the flexibility to either utilize a component class for data preparation or directly pass the data to the component. The default implementation provides a straightforward way to get started with tracking visualizations in your Django admin interface.

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

Let's examine an example of a component class that handles data preparation for the tracker component. When implementing this class, you'll need to create a method that prepares and structures the data appropriately. The component in your template will receive this data through the `data` parameter, which is passed to the `get_context_data` method. This approach provides a clean separation between data preparation logic and presentation, making your code more maintainable and easier to test.

```python
# admin.py

from unfold.components import BaseComponent, register_component


@register_component
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
