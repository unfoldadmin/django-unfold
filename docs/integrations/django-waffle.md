---
title: django-waffle
order: 0
description: djagno-waffle integration guide for Unfold
---

# django-waffle

To use django-waffle with Django Unfold, you should first unregister the default admin classes provided by django-waffle. Then, register them again but inherit from Unfold's `unfold.model.ModelAdmin` to take advantage of Unfold's improved admin interface.

For the `FlagAdmin`, however, Unfold provides its own custom admin class (`unfold.contrib.waffle.admin.FlagAdmin`) because the `users` field in django-waffle uses a custom implementation, which Unfold replaces with an autocomplete widget to enhance usability.

Unregister the default Waffle admin models and register them again using Unfold's admin classes.

```python
# admin.py

from django.contrib import admin

from waffle.admin import SampleAdmin as BaseSampleAdmin
from waffle.admin import SwitchAdmin as BaseSwitchAdmin
from waffle.models import Flag, Sample, Switch

from unfold.admin import ModelAdmin

# This is custom admin class for Flag model
from unfold.contrib.waffle.admin import FlagAdmin as BaseFlagAdmin

# Unregister default admin classes
admin.site.unregister(Flag)
admin.site.unregister(Switch)
admin.site.unregister(Sample)


# Note: we are inheriting from Unfold's BaseFlagAdmin
@admin.register(Flag)
class FlagAdmin(BaseFlagAdmin):
    pass


@admin.register(Switch)
class SwitchAdmin(ModelAdmin, BaseSwitchAdmin):
    pass


@admin.register(Sample)
class SampleAdmin(ModelAdmin, BaseSampleAdmin):
    pass
```
