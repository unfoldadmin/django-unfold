---
title: Component class
order: 1
description: Create and register custom component classes in Django Unfold to preprocess data before rendering, separating business logic from presentation templates for cleaner, more maintainable code.
---

# Component class

Unfold's component system features specialized component classes designed to preprocess and prepare data for rendering. These component classes are completely optional - you have the flexibility to either leverage them for handling data preparation logic or bypass them entirely by passing data directly to components in your templates. The choice depends on your specific needs and preferences for each use case.

## Component registration

For Unfold to recognize and utilize your custom component classes, each class must be registered within the system using the `register_component` decorator. This registration process is essential as it makes your component discoverable by Unfold's component rendering system, allowing it to be referenced by name in templates.

The registration mechanism creates a mapping between the component class name and its implementation, enabling the template engine to instantiate the correct class when the component is invoked. Without proper registration, Unfold would be unable to locate your component class when referenced in template files.

```python
# admin.py

from unfold.components import BaseComponent, register_component


@register_component
class MyComponent(BaseComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "data": DATA
        })
        return context
```

## Using component classes in templates

After registering your component class, you can reference it in your templates by its class name. This is done using the `component_class` parameter when invoking a component. When the template is rendered, Unfold will automatically instantiate the specified component class, execute its `get_context_data` method, and pass the resulting context to the component template.

This approach allows you to separate your data preparation logic from your presentation templates, promoting cleaner code organization and reusability. The component class handles all the data processing, while the template focuses solely on rendering the prepared data.

```html
{% load unfold %}

{% component "unfold/components/my_component.html" with component_class="MyComponent" %}{% endcomponent %}
```
