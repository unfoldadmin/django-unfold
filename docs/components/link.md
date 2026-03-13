---
title: Component - Link
order: 5
description: Guide to the Unfold Link component for Django, featuring accessible, icon-supported links with external link handling.
---

# Link component

The Link component provides a styled anchor (`<a>`) element that fits seamlessly with the Unfold interface. It allows you to display an optional icon next to the link text, making links easier to identify and interact with.

You can also mark a link as external, which will open it in a new tab and display an external link icon for added clarity. This ensures users always know when they're leaving your site or navigating to a different resource.

```html
{% load unfold %}

{% component "unfold/components/link.html" with href="https://example.com" icon="start" external=1 %}
    {% trans "Link text" %}
{% endcomponent %}
```

## Example with the card component

This example shows how to display a list of links inside a card component. The card includes extra configuration to improve its visual appeal and layout.

```html
{% load unfold %}

{% trans "Card title to display" as features_title %}

{% capture as features_action silent %}
    {% component "unfold/components/button.html" with href="#" variant="default" size="sm" %}
        {% trans "View more" %}
    {% endcomponent %}
{% endcapture %}

{% component "unfold/components/card.html" with title=features_title action=features_action title_class="!py-3" %}
    <div class="flex flex-col gap-5">
        {% component "unfold/components/link.html" with href="https://example.com" icon="start" external=1 %}
            {% trans "Example link 1" %}
        {% endcomponent %}

        {% component "unfold/components/link.html" with href="https://example.com" icon="start" external=1 %}
            {% trans "Example link 2" %}
        {% endcomponent %}
    </div>
{% endcomponent %}
```

## Link component parameters

| Parameter   | Description                                                           |
|-------------|-----------------------------------------------------------------------|
| href        | Link URL. If not provided, the link is displayed without an href      |
| icon        | Icon to display                                                       |
| external    | If set, opens the link in a new tab and shows an external link icon   |
| class       | Additional CSS classes                                                |
