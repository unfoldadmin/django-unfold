---
title: Introduction to components
order: 0
description: Components overview for in Unfold theme
---

# Introduction to components

Unfold provides a set of already predefined templates to speed up overall dashboard development. These templates contain predefined design which matches global design style so there is no need to spend any time adjusting styles.

The biggest benefit of Unfold components is the possibility to nest them inside one template file provides an unlimited amount of possible combinations. Then each component includes `children` variable which contains a value specified in the parent component. Except for `children` variable, components can have multiple variables coming from the parent template as component variables. These parameters can be specified in the same as parameters when using `{% include with param1=value1 param2=value2 %}` template tag.

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

Below you can find a more complex example which is using multiple components and processing them based on the passed variables from the `DASHBOARD_CALLBACK`.

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
| unfold/components/cohort.html     | Cohort component               | data                                 |


## Table component example

```python
from typing import Dict
from django.http import HttpRequest


def dashboard_callback(request: HttpRequest) -> Dict:
    return {
        "table_data": {
            "headers": ["col 1", "col 2"],
            "rows": [
                ["a", "b"],
                ["c", "d"],
            ]
        }
    }
```

```html
{% load unfold %}

{% component "unfold/components/card.html" with title="Card title" %}
    {% component "unfold/components/table.html" with table=table_data card_included=1 striped=1 %}{% endcomponent %}
{% endcomponent %}
```
