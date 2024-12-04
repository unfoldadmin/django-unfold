---
title: Custom pages
order: 10
description: Custom admin pages for Unfold.
---

# Custom pages

By default, Unfold provides a basic view mixin which helps with creation of basic views which are part of Unfold UI. The implementation requires creation of class based view inheriting from `unfold.views.UnfoldModelAdminViewMixin`. It is important to add `title` and `permission_required` properties.

```python
# admin.py

from django.views.generic import TemplateView
from unfold.admin import ModelAdmin
from unfold.views import UnfoldModelAdminViewMixin
from .models import MyModel


class MyClassBasedView(UnfoldModelAdminViewMixin, TemplateView):
    title = "Custom Title"  # required: custom page header title
    permission_required = () # required: tuple of permissions
    template_name = "some/template/path.html"


@admin.register(MyModel)
class CustomAdmin(ModelAdmin):
    def get_urls(self):
        return super().get_urls() + [
            path(
                "custom-url-path",
                MyClassBasedView.as_view(model_admin=self),  # IMPORTANT: model_admin is required
                name="custom_name"
            ),
        ]
```

The template is straightforward, extend from `unfold/layouts/base.html` and the UI will display all Unfold components like header or sidebar with all menu items. Then all content needs to be located in `content` block.

```html
{% extends "unfold/layouts/base.html" %}

{% block content %}
    Content here
{% endblock %}
```

**Note:** custom view is not by default added into sidebar navigation. It has to be added manually into sidebar in **UNFOLD** settings.
