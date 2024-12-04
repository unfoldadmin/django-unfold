---
title: Quickstart
order: 1
description: Quickstard installation guide for Unfold.
---

# Quickstart

The installation process is minimal. Everything that is needed after installation is to put new application at the beginning of **INSTALLED_APPS**. The default admin configuration in urls.py can stay as it is, and no changes are required.

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

In case you need installation command below are the versions for `pip` and `poetry` which needs to be executed in shell.

```bash
pip install django-unfold
poetry add django-unfold
```

Just for an example below is the minimal admin configuration in terms of adding Unfold into URL paths.

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

After installation, it is required that admin classes are going to inherit from custom `unfold.admin.ModelAdmin`. The default `django.contrib.admin.ModelAdmin` will not work with Unfold and it will cause unstyles forms and missing functionality.

```python
# admin.py

from django.contrib import admin
from unfold.admin import ModelAdmin


@admin.register(MyModel)
class CustomAdminClass(ModelAdmin):
    pass
```
