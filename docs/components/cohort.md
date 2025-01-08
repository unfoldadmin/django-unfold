---
title: Component - Cohort
order: 2
description: Cohort component in Unfold theme
---

# Cohort component

The cohort component allows you to display cohort analysis data in a table format. It's useful for analyzing user behavior and retention over time. Unfold provides a default implementation of the cohort component. The only important parameter is the `data` parameter, which is a dictionary that contains a more complex data structure.


## Default cohort component implementation in template

In template you can use the default implementation of the cohort component by using the following code below. The `component_class` parameter is the name of the component class that you will create in the next section and it will prepare the data for the cohort component.

```html
{% load unfold %}

{% component "unfold/components/chart/cohort.html" with component_class="MyCohortComponent" %}
{% endcomponent %}
```

If you don't want to use `component_class` parameter, you can prepare `data` in the dashboard callback function and use it like this:

```html
{% load unfold %}

{% component "unfold/components/chart/cohort.html" with data=my_data_variable data=my_data %}
{% endcomponent %}
```

## Custom cohort data preparation in component class

Below you can see an example of a component class that prepares the data for the cohort component. The component in template will receive the `data` parameter that is passed to the `get_context_data` method.

```python
# admin.py

from unfold.components import BaseComponent

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
        "header": {
            # Row heading
            "title": "Title",
                "subtitle": "something",  # Optional
            },
            # Col 1 cell value
            "cols": [
                {
                    "value": "1",
                }
            ]
        },
    ]
}
```
