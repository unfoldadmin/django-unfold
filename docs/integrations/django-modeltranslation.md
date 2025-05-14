---
title: django-modeltranslation
order: 0
description: Learn how to integrate django-modeltranslation with Django Unfold admin panel to manage multilingual content with tabbed navigation, custom language flags, and enhanced translation management features for a seamless localization experience.
---

# django-modeltranslation

Unfold provides built-in support for django-modeltranslation, a powerful Django application that enables model translation functionality. The integration includes a custom implementation of the `TabbedTranslationAdmin` admin class, which provides tabbed navigation for managing translations with Unfold's enhanced styling and user interface components. This seamless integration ensures that translation management maintains visual consistency with the rest of your admin interface while providing all the powerful features of django-modeltranslation.

```python
from django.contrib import admin

from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin

from .models import MyModel


@admin.register(MyModel)
class MyModelAdmin(ModelAdmin, TabbedTranslationAdmin):
    pass
```

For django-modeltranslation fields for specific languages, it is possible to define custom flags which will appear as a suffix in each field's label. These flags help visually distinguish between different language versions of the same field. While you can use any text or symbol as a suffix, it is recommended to use emojis as they provide clear visual indicators without taking up much space. The flags will be displayed next to the field labels in the admin interface, making it easy for content editors to identify which language version they are currently editing.

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

For comprehensive information about installation, configuration, and usage of django-modeltranslation, please refer to the [official documentation](https://django-modeltranslation.readthedocs.io/en/latest/). The documentation covers everything from basic setup to advanced features like model translation, field registration, and customizing translation behavior. You'll find detailed guides on how to implement translations for your models, configure language settings, and manage translations through the admin interface.

[![Django Modeltranslation](/static/docs/integrations/django-modeltranslation.webp)](/static/docs/integrations/django-modeltranslation.webp)

A live demo of the django-modeltranslation integration with Unfold is available at [https://demo.unfoldadmin.com/en/admin/formula/driver/56/change/](https://demo.unfoldadmin.com/en/admin/formula/driver/56/change/). This demo showcases how Unfold seamlessly integrates with django-modeltranslation's translation interface, providing an enhanced user experience for managing multilingual content.
