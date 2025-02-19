---
title: Custom sites
order: 11
description: Create and customize admin sites in Django Unfold, including overriding the default admin site and registering models with custom admin sites.
---

# Custom sites

In order to create a custom admin site, Unfold provides the `unfold.sites.UnfoldAdminSite` class which can be used as follows:

```python
# sites.py

from django.contrib import admin
from unfold.sites import UnfoldAdminSite

class CustomAdminSite(UnfoldAdminSite):
    pass


custom_admin_site = CustomAdminSite(name="custom_admin_site")
```

```python
# urls.py

from django.urls import path
from .sites import custom_admin_site


urlpatterns = [
    # other URL patterns
    path("admin/", custom_admin_site.urls),
]
```

```python
# models.py

from django.contrib.auth.models import User
from unfold.admin import ModelAdmin


@admin.register(User, site=custom_admin_site)
class UserAdmin(ModelAdmin):
    model = User
```

**Note**: If you use the default `django.contrib.admin.AdminSite` you will receive a `NoReverseMatch` error because the default admin site does not contain all URL patterns required by Unfold.

## Overriding the default admin site

If you want to override the default admin site by setting the `default_site` attribute of a custom `django.contrib.admin.apps.AdminConfig` class, you must install Unfold using `unfold.apps.AppConfig` instead of just `unfold` in `INSTALLED_APPS`.

```python
# settings.py

INSTALLED_APPS = [
    "unfold.apps.BasicAppConfig", # App config not overriding `django.contrib.admin.site`
    # some other apps
    "django.contrib.admin",
    "your_app",
]
```

```python
# apps.py

from django.contrib.admin.apps import AdminConfig


class MyAdminConfig(AdminConfig):
    default_site = "myproject.sites.CustomAdminSite"
```
