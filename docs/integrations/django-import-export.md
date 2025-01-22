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
