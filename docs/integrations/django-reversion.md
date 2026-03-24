---
title: django-reversion
order: 0
description: Integrate django-reversion and django-reversion-compare with Django Unfold to style object history, recover flows, and version comparison screens in the admin interface.
---

# django-reversion

To integrate django-reversion with Unfold, add `unfold.contrib.reversion` to your `INSTALLED_APPS` setting after `unfold` and before `reversion`. If you also use django-reversion-compare, keep `unfold.contrib.reversion` before `reversion_compare` as well so Unfold's template overrides take precedence.

```python
# settings.py

INSTALLED_APPS = [
    "unfold",
    # ...
    "unfold.contrib.reversion",
    # ...
    "reversion",
    "reversion_compare",  # optional
]
```

For plain django-reversion history and recover flows, inherit from both `VersionAdmin` and `unfold.admin.ModelAdmin` in your admin configuration:

```python
# admin.py

from django.contrib import admin
from reversion.admin import VersionAdmin

from unfold.admin import ModelAdmin

from .models import ExampleModel


@admin.register(ExampleModel)
class ExampleAdmin(VersionAdmin, ModelAdmin):
    pass
```

If you also want side-by-side version comparison, inherit from `CompareVersionAdmin` instead:

```python
# admin.py

from django.contrib import admin
from reversion_compare.admin import CompareVersionAdmin

from unfold.admin import ModelAdmin

from .models import ExampleModel


@admin.register(ExampleModel)
class ExampleCompareAdmin(CompareVersionAdmin, ModelAdmin):
    pass
```
