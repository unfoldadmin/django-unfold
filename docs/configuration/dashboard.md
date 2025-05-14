---
title: Dashboard
order: 10
description: Create a customized Django Unfold admin dashboard with dynamic charts, components, data visualization, and personalized content using template overrides and Tailwind CSS styling for an enhanced admin interface.
---

# Admin dashboard

To customize your admin dashboard, start by creating a new file at `templates/admin/index.html` in your project directory. This file will serve as your custom dashboard template. You can use the base template provided below as a starting point for your customization.

It's important to note that when you add custom styles to this template, they won't be automatically compiled and applied. This is because the CSS classes are specific to your project rather than being part of the core Unfold package. To properly implement your custom styling, you'll need to configure Tailwind CSS for your project or you can write your own custom CSS styles without using Tailwind at all.

For detailed instructions on setting up Tailwind CSS and ensuring your custom styles are properly compiled and applied, please refer to our comprehensive guide in the [Project Level Tailwind Stylesheet](https://unfoldadmin.com/docs/styles-scripts/customizing-tailwind/) chapter. This guide will walk you through the necessary steps to integrate Tailwind with your project and enable custom styling for your dashboard.

Ensure you have set up the template directory in `settings.py`

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # Ensure this line is added
        #....
    }
```

```html
{% extends 'admin/base.html' %}

{% load i18n %}

{% block breadcrumbs %}{% endblock %}

{% block title %}
    {% if subtitle %}
        {{ subtitle }} |
    {% endif %}

    {{ title }} | {{ site_title|default:_('Django site admin') }}
{% endblock %}

{% block branding %}
    {% include "unfold/helpers/site_branding.html" %}
{% endblock %}

{% block content %}
    Start creating your own Tailwind components here
{% endblock %}
```

## Custom variables

When building a new dashboard, you'll often need to display data from your database. Unfold provides a special `DASHBOARD_CALLBACK` parameter that allows you to pass custom variables to your `templates/admin/index.html` template through a dictionary.

```python
# views.py

def dashboard_callback(request, context):
    context.update({
        "custom_variable": "value",
    })

    return context
```

```python
# settings.py

UNFOLD = {
    "DASHBOARD_CALLBACK": "app.views.dashboard_callback",
}
```
