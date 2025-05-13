---
title: Introduction to components
order: 0
description: Comprehensive guide to Django Unfold's component system, featuring nested templates, dynamic data handling, and customizable layouts. Learn how to build powerful admin dashboards using reusable components with seamless design system integration.
---

# Introduction to components

Unfold comes with a comprehensive set of predefined templates designed to accelerate dashboard development. These templates feature carefully crafted designs that seamlessly integrate with the global design system, eliminating the need for time-consuming style adjustments.

One of the most powerful features of Unfold components is their ability to be nested within a single template file, enabling virtually unlimited layout combinations. Each component has access to a `children` variable that contains content specified by its parent component. Beyond the `children` variable, components can receive multiple variables from their parent template as component parameters. These parameters can be passed in the same way as Django template parameters using the `{% include with param1=value1 param2=value2 %}` template tag syntax. This flexibility allows for highly customizable and reusable component structures while maintaining clean and organized templates.

```html
{% load unfold %}

<div class="flex flex-col">
    {% component "unfold/components/card.html" %}
        {% component "unfold/components/title.html" %}
            Card Title
        {% endcomponent %}
    {% endcomponent %}
</div>
```

Let's explore a more sophisticated example that demonstrates how multiple components can work together seamlessly. This example showcases component nesting and dynamic data processing, where components receive and handle variables passed from the `DASHBOARD_CALLBACK`. The example below illustrates how to create a complex, interactive dashboard layout while maintaining clean and readable code structure.

```html
{% load i18n unfold %}

{% block content %}
    {% component "unfold/components/container.html" %}
        <div class="flex flex-col gap-4">
            {% component "unfold/components/navigation.html" with items=navigation %}
            {% endcomponent %}

            {% component "unfold/components/navigation.html" with class="ml-auto" items=filters %}
            {% endcomponent %}
        </div>

        <div class="grid grid-cols-3">
            {% for card in cards %}
                {% trans "Last 7 days" as label %}
                {% component "unfold/components/card.html" with class="lg:w-1/3" %}
                    {% component "unfold/components/text.html" %}
                        {{ card.title }}
                    {% endcomponent %}

                    {% component "unfold/components/title.html" %}
                        {{ card.metric }}
                    {% endcomponent %}
                {% endcomponent %}
            {% endfor %}
        </div>
    {% endcomponent %}
{% endblock %}
```

## List of available components

| Component                         | Description                    | Arguments                            |
| --------------------------------- | ------------------------------ | ------------------------------------ |
| unfold/components/button.html     | Basic button element           | class, name, href, submit            |
| unfold/components/card.html       | Card component                 | class, title, footer, label, icon    |
| unfold/components/chart/bar.html  | Bar chart implementation       | class, data, height, width           |
| unfold/components/chart/line.html | Line chart implementation      | class, data, height, width           |
| unfold/components/cohort.html     | Cohort component               | data                                 |
| unfold/components/container.html  | Wrapper for settings max width | class                                |
| unfold/components/flex.html       | Flex items                     | class, col                           |
| unfold/components/icon.html       | Icon element                   | class                                |
| unfold/components/navigation.html | List of navigation links       | class, items                         |
| unfold/components/progress.html   | Percentual progress bar        | class, value, title, description     |
| unfold/components/separator.html  | Separator, horizontal rule     | class                                |
| unfold/components/table.html      | Table                          | table, card_included, striped        |
| unfold/components/text.html       | Paragraph of text              | class                                |
| unfold/components/title.html      | Basic heading element          | class                                |
| unfold/components/tracker.html    | Tracker component              | data                                 |
