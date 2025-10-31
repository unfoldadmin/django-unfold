---
title: Component - Card
order: 3
description: Explore the features and customization options of the Unfold card component
---

# Card component

A card is a versatile content container used to visually separate and organize distinct sections within your layout. It helps to group related information, making your dashboard or page easier to read and navigate. Use the card component whenever you want to highlight or isolate content in a clean and structured manner.

```html
{% load i18n unfold %}

{% trans "Card component title" as custom_title %}

{% capture as custom_action %}
    {% component "unfold/componentes/button.html" %}
        Do something
    {% endcomponent}
{% endcapture %}

{% component "unfold/components/card.html" with title=custom_title action=custom_action %}
    Children elements here
{% endcomponent %}
```

| Parameter       | Description                                                               |
| --------------- | ------------------------------------------------------------------------- |
| title           | Card title displayed at the top                                           |
| label           | Floating label displayed in the top right                                 |
| action          | Content on the same row as the title, on the right                        |
| icon            | Background icon with negative spacing. Ideal for small KPI cards          |
| footer          | Custom text displayed at the bottom of the card                           |
| href            | Link that makes the card clickable                                        |
| disable_border  | Card border will not be displayed. Ideal for cards on primary backgrounds |
| class           | Additional CSS classes                                                    |
