---
title: django-import-export
order: 0
description: Integration with django-import-export.
---

# django-import-export

1. Add `unfold.contrib.import_export` to `INSTALLED_APPS` at the beginning of the file. This action will override all templates coming from the application.
2. Change `import_form_class` and `export_form_class` in ModelAdmin which is inheriting from `ImportExportModelAdmin`. This chunk of code is responsible for adding proper styling to form elements.

```python
# admin.py

from unfold.admin import ModelAdmin
from import_export.admin import ImportExportModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm, SelectableFieldsExportForm

class ExampleAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    # export_form_class = SelectableFieldsExportForm
```

When implementing `import_export.admin.ExportActionModelAdmin` class in admin panel, import_export plugin adds its own implementation of action form which is not incorporating Unfold CSS classes. For this reason, `unfold.contrib.import_export.admin` contains class with the same name `ExportActionModelAdmin` which inherits behavior of parent form and adds appropriate CSS classes.

**Note:** This class has been removed and in new version (4.x) of django-import-export it is not needed.

```python
admin.py

from unfold.admin import ModelAdmin
from unfold.contrib.import_export.admin import ExportActionModelAdmin

class ExampleAdmin(ModelAdmin, ExportActionModelAdmin):
    pass
```

### django-modeltranslation

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
