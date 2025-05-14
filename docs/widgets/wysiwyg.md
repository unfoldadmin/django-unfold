---
title: WysiwygWidget
order: 2
description: Integrate Django Unfold's WysiwygWidget, a rich text editor powered by Trix, to enhance text fields in your Django admin interface with elegant formatting capabilities and a user-friendly editing experience.
---

# Unfold widget WysiwygWidget

To enhance your Django admin interface with rich text editing capabilities, you'll need to integrate the WysiwygWidget component. This requires adding `unfold.contrib.forms` to your project's `INSTALLED_APPS` setting as a mandatory dependency. The WysiwygWidget leverages the powerful [Trix editor](https://trix-editor.org/), an elegant open-source rich text editor that provides a clean and intuitive interface for content creation. Trix offers essential formatting options while maintaining simplicity and ease of use, making it an excellent choice for managing text content in your Django admin interface.

[![Wysiwyg widget](/static/docs/widgets/wysiwyg.webp)](/static/docs/widgets/wysiwyg.webp)

```python
# settings.py

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.forms",
]
```

The following example demonstrates how to enhance all `TextField` fields in your admin interface by replacing them with the `WysiwygWidget`. This is achieved by using the `formfield_overrides` setting in your ModelAdmin class, which automatically applies the rich text editor to every text field. While the `WysiwygWidget` currently doesn't include built-in file upload functionality, you can still incorporate images into your content by first uploading them through your regular media management system and then inserting the image URL into the editor. This provides a flexible workflow for managing both text and media content within your admin interface.

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
