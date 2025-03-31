---
title: Component - Cohort
order: 2
description: A powerful visualization component for cohort analysis that displays user behavior patterns over time in a structured table format, perfect for tracking retention and engagement metrics in Django Unfold admin.
---

# Cohort component

The cohort component is a powerful visualization tool that presents cohort analysis data in a structured table format. It enables you to track and analyze how groups of users (cohorts) behave over specific time periods, making it particularly valuable for measuring retention, engagement patterns, and user lifecycle metrics. Unfold provides a ready-to-use implementation of this component that requires minimal setup. To use it, you only need to provide the `data` parameter - a dictionary containing the cohort information with a specific structure that defines headers, rows, and cell values for the analysis table.


## Default cohort component implementation in template

You can use the default implementation of the cohort component in your template with the following code. The `component_class` parameter refers to the name of the component class that will prepare the data for the cohort component, which we'll create in the next section.

```html
{% load unfold %}

{% component "unfold/components/chart/cohort.html" with component_class="MyCohortComponent" %}
{% endcomponent %}
```

Alternatively, if you prefer not to use the `component_class` parameter, you can prepare the `data` directly in your dashboard callback function and pass it to the component like this:

```html
{% load unfold %}

{% component "unfold/components/chart/cohort.html" with data=my_data_variable %}
{% endcomponent %}
```

## Custom cohort data preparation in component class

Here's an example of a component class that prepares data for the cohort component. When used in a template, the component will receive the `data` parameter that has been processed and returned by the `get_context_data` method.

```python
# admin.py

from unfold.components import BaseComponent, register_component

@register_component
class MyCohortComponent(BaseComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "data": DATA
        })
        return context
```

## Data structure example

```python
DATA = {
    "headers": [
        # Col 1 header
        {
            "title": "Title",
            "subtitle": "something",  # Optional
        },
    ],
    "rows": [
        # First row
        {
            # Row heading
            "header": {
                "title": "Title",
                "subtitle": "something",  # Optional
            },
            "cols": [
                # Col 1 cell value
                {
                    "value": "1",
                    "subtitle": "something",  # Optional
                }
            ]
        },
        # Second row
        {
            # Row heading
            "header": {
                "title": "Title",
                "subtitle": "something",  # Optional
            },
            "cols": [
                # Col 1 cell value
                {
                    "value": "1",
                }
            ]
        },
    ]
}
```
