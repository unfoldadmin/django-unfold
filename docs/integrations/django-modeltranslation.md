---
title: django-modeltranslation
order: 0
description: Integration with django-modeltranslation.
---

# django-modeltranslation

By default, Unfold supports django-modeltranslation and `TabbedTranslationAdmin` admin class for the tabbed navigation is implemented with custom styling as well.

```python
from django.contrib import admin

from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin

from .models import MyModel


@admin.register(MyModel)
class MyModelAdmin(ModelAdmin, TabbedTranslationAdmin):
    pass
```

For django-modeltranslation fields for spefic languages, it is possible to define custom flags which will appear as a suffix in field's label. It is recommended to use emojis as suffix.

```python
# settings.py

UNFOLD = {
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "nl": "🇧🇪",
            },
        },
    },
}
```
