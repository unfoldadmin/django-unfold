---
title: Custom sites
order: 11
description: Custom admin sites for Unfold.
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

Note: If you use the default `django.contrib.admin.AdminSite` you will receive a `NoReverseMatch` error because the default admin site does not contain all URL patterns required by Unfold.
