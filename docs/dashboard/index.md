---
title: Dashboard
order: 10
description: Customize admin dashboard with your own charts and components.
---

# Admin dashboard

Create `templates/admin/index.html` in your project and paste the base template below into it. By default, all your custom styles here are not compiled because CSS classes are located in your specific project. Here it is needed to set up the Tailwind for your project and all required instructions are located in [Project Level Tailwind Stylesheet](https://unfoldadmin.com/docs/styles-scripts/customizing-tailwind/) chapter.

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
{% extends 'unfold/layouts/base_simple.html' %}

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

When you are building a new dashboard, you need to display some data mostly coming from the database. To pass these data to the dashboard template, Unfold contains a special `DASHBOARD_CALLBACK` parameter which allows passing a dictionary of variables to `templates/admin/index.html` template.

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
