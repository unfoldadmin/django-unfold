---
title: Component class
order: 1
description: Component class for custom component preprocessing
---

# Component class

Each component in Unfold theme has a component class that is responsible for preparing the data for the component. The component class is optional and if you don't want to use it, you can pass the data directly to the component in the template.

```python
# admin.py

from unfold.components import BaseComponent

class MyComponent(BaseComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "data": DATA
        })
        return context
```

You can then use the component class in your template like this:

```html
{% load unfold %}

{% component "unfold/components/my_component.html" with component_class="MyComponent" %}{% endcomponent %}
```
