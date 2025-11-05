---
title: Component - Chart
order: 4
description: Add bar and line charts to Django with Unfold’s customizable Chart.js component and built-in design integration.
---

# Chart component

Unfold provides built-in components for easily rendering bar and line charts. Simply pass a properly structured data object to the chart component and it will be displayed automatically. Chart rendering is handled by Chart.js with default configurations that match the Unfold design system. Basic settings can be adjusted without modifying code. For advanced customization, use the `options` parameter to provide your own Chart.js options (except for JavaScript functions, which are not supported).

## Special options

- To configure the maximum number of ticks on the X-axis, add the `maxTicksXLimit` property to the dataset.
- By default, Y-axis labels are hidden. To display them, add the `displayYAxis` property to the dataset.
- To show a suffix on Y-axis values, add the `suffixYAxis` property to the dataset.

```python
# admin.py

from unfold.components import BaseComponent


@register_component
class BarChartComponent(BaseComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "height": 320,
            "data": json.dumps({
                "labels": ["Mo", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                "datasets": [
                    {
                        "label": "Dataset 1",
                        "data": [12, 19, 3, 5, 2, 3, 9],
                        "backgroundColor": "var(--color-primary-700)",
                    },
                    {
                        "label": "Dataset 2",
                        "data": [3, 12, 5, 9, 2, 19, 3],
                        "borderColor": "var(--color-primary-400)",
                        "type": "line",  # Change the type here
                        # "displayYAxis": True,  # Display the Y-axis labels
                        # "maxTicksXLimit": 50,  # Limit the number of ticks on X-axis
                        # "suffixYAxis": "€",  # Add a suffix to the Y-axis values
                    }
                ]
            })
            # Completely custom chart options
            # "options": json.dumps({
            #   "sample": "example",
            # })
        })

        return context
```

```html
{% load unfold %}

{% component "unfold/components/card.html" with title="Chart title" %}
    {% component "unfold/components/chart/bar.html" with component_class="BarChartComponent" %}{% endcomponent %}
{% endcomponent %}
```
