---
title: django-import-export
order: 0
description: Integrate django-import-export with Django Unfold admin panel to enable seamless data import and export functionality, custom form styling, and enhanced user experience for managing data transfers in various formats.
---

# django-import-export

To integrate django-import-export with Unfold's admin interface, follow these two key steps:

1. Add `unfold.contrib.import_export` to your project's `INSTALLED_APPS` setting at the beginning of the settings file. This will ensure that all templates from django-import-export are properly overridden with Unfold's styling and components, maintaining a consistent look and feel throughout your admin interface.

2. When configuring your ModelAdmin class that inherits from `ImportExportModelAdmin`, you'll need to specify the `import_form_class` and `export_form_class` attributes. These custom form classes provided by Unfold add proper styling to all form elements, ensuring they match Unfold's design system. The forms handle both the import functionality for bringing data into your application and export functionality for extracting data in various formats.

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

When implementing the `import_export.admin.ExportActionModelAdmin` class in your admin panel, the django-import-export plugin adds its own implementation of the action form. However, this default implementation does not incorporate Unfold's CSS classes, which can lead to inconsistent styling in your admin interface. To address this, `unfold.contrib.import_export.admin` provides a custom `ExportActionModelAdmin` class that inherits all the behavior of the parent form while adding the appropriate Unfold CSS classes to maintain visual consistency.

The custom implementation ensures that action forms maintain the same look and feel as the rest of your Unfold admin interface, providing a seamless user experience when working with import/export functionality.

**Note:** This class has been removed in version 4.x of django-import-export as the styling inconsistencies have been addressed in the core package. If you are using django-import-export 4.x or later, you can use the default `ExportActionModelAdmin` class directly without any styling concerns.

```python
# admin.py

from unfold.admin import ModelAdmin
from unfold.contrib.import_export.admin import ExportActionModelAdmin

# Not needed in django-import-export 4.x+
class ExampleAdmin(ModelAdmin, ExportActionModelAdmin):
    pass
```

For comprehensive information about installation, configuration, and usage of django-import-export, please refer to the [official documentation](https://django-import-export.readthedocs.io/en/latest/). The documentation covers everything from basic setup to advanced features like customizing import/export formats, handling data transformations, and configuring resource classes. You'll find detailed guides on implementing import/export functionality in your models and customizing the behavior to match your specific needs.

[![Django Import Export 1](/static/docs/integrations/django-import-export-1.webp)](/static/docs/integrations/django-import-export-1.webp)

[![Django Import Export 2](/static/docs/integrations/django-import-export-2.webp)](/static/docs/integrations/django-import-export-2.webp)

A live demo of the django-import-export integration with Unfold is available at [https://demo.unfoldadmin.com/en/admin/formula/constructor/](https://demo.unfoldadmin.com/en/admin/formula/constructor/). This demo showcases how Unfold seamlessly integrates with django-import-export's import and export functionality, providing an enhanced user experience for data management. You can explore features like importing data from various formats, exporting selected records, and customizing import/export fields through the intuitive admin interface.
