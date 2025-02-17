---
title: WysiwygWidget
order: 2
description: WysiwygWidget for TextField
---

# Unfold widget WysiwygWidget

To use WysiwygWidget, you need to have `unfold.contrib.forms` in `INSTALLED_APPS` which is required dependency. The WYSIWYG widget is based on [Trix editor](https://trix-editor.org/).

```python
# settings.py

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.forms",
]
```

Below is simple example replacing all `TextField` fields with `WysiwygWidget` in admin particular admin class. At the moment `WysiwygWidget` does not support file upload but it is still possible to manually upload an image and then link it into the content area.

```python
# admin.py

from django.db import models
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget


@admin.register(MyModel)
class CustomAdminClass(ModelAdmin):
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }
```
