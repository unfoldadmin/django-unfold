---
title: Quickstart
order: 1
description: Step-by-step guide to install and configure Django Unfold admin interface in your Django project, including package installation, INSTALLED_APPS configuration, and ModelAdmin setup.
---

# Quickstart

The installation process is straightforward. After installing the package, you only need to add the Unfold application to the beginning of your **INSTALLED_APPS** setting. The default admin configuration in urls.py can remain unchanged.

```python
# settings.py

INSTALLED_APPS = [
    "unfold",  # before django.contrib.admin
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.inlines",  # optional, if special inlines are needed
    "unfold.contrib.import_export",  # optional, if django-import-export package is used
    "unfold.contrib.guardian",  # optional, if django-guardian package is used
    "unfold.contrib.simple_history",  # optional, if django-simple-history package is used
    "django.contrib.admin",  # required
]
```

To install Django Unfold in your project, you can use any of the popular Python package managers. Below are the installation commands for `pip`, `uv`, and `poetry`. Execute the appropriate command in your terminal based on your preferred package manager:

```bash
pip install django-unfold
uv add django-unfold
poetry add django-unfold
```

Below is an example of the minimal URL configuration needed to integrate Unfold into your Django project:

```python
# urls.py

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Other URL paths
]
```

## ModelAdmin inheritance

After installation, your admin classes must inherit from `unfold.admin.ModelAdmin` instead of the default `django.contrib.admin.ModelAdmin`. Using the default admin class will result in unstyled forms and missing Unfold functionality.

```python
# admin.py

from django.contrib import admin
from unfold.admin import ModelAdmin


@admin.register(MyModel)
class CustomAdminClass(ModelAdmin):
    pass
```
