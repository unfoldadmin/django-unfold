---
title: Custom pages
order: 10
description: Create custom admin pages in Django Unfold with custom views, templates, breadcrumbs and tabs. Extend your Django admin interface with custom pages.
---

# Custom pages

By default, Unfold provides a basic view mixin which helps with creation of basic views which are part of Unfold UI. The implementation requires creation of class based view inheriting from `unfold.views.UnfoldModelAdminViewMixin`. It is important to add `title` and `permission_required` properties.

```python
# admin.py

from django.urls import path
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
        # IMPORTANT: model_admin is required
        custom_view = self.admin_site.admin_view(
            MyClassBasedView.as_view(model_admin=self)
        )

        return super().get_urls() + [
            path(
                "custom-url-path", custom_view, name="custom_name"
            ),
        ]
```

The template is straightforward, extend from `unfold/layouts/base.html` and the UI will display all Unfold components like header or sidebar with all menu items. Then all content needs to be located in `content` block. Below you can find full example from the Formula project implementing additional components:

- Breadcrumbs: it is up to developer to construct own breadcrumbs
- Tab list: in case your project has dynamic tabs, you can use `tab_list` helper to display them

```html
{% extends "unfold/layouts/base.html" %}

{% load admin_urls i18n unfold %}

{% block breadcrumbs %}{% if not is_popup %}
    <div class="px-4 lg:px-8">
        <div class="container mb-6 mx-auto -my-3 lg:mb-12">
            <ul class="flex flex-wrap">
                {% url 'admin:index' as link %}
                {% trans 'Home' as name %}
                {% include 'unfold/helpers/breadcrumb_item.html' with link=link name=name %}

                {% url 'admin:formula_driver_changelist' as link %}
                {% trans 'Drivers' as name %}
                {% include 'unfold/helpers/breadcrumb_item.html' with link=link name=name %}

                {% trans 'Custom page' as name %}
                {% include 'unfold/helpers/breadcrumb_item.html' with name=name %}
            </ul>
        </div>
    </div>
{% endif %}{% endblock %}

{% block content %}
    {% tab_list "drivers" %}

    {% trans "Custom page" %}
{% endblock %}
```

**Note:** custom view is not by default added into sidebar navigation. It has to be added manually into sidebar in **UNFOLD** settings.
