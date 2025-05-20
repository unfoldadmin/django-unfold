---
title: JsonField
order: 0
description: Implement and customize JSON field formatting and syntax highlighting in Django Unfold admin interface, with PrettyJSONEncoder for basic formatting and enhanced display through Pygments integration.
---

# JsonField formatting and syntax highlighting

Unfold currently provides basic JSON formatting and syntax highlighting, but only when the JSON field is included in the admin configuration's `readonly_fields` list. For fields not marked as read-only, Unfold displays them as plain text using the `UnfoldAdminTextareaWidget`.

When a JSON field is both marked as read-only and the Pygments library is installed (via `pip install pygments`), Unfold will display the field with syntax highlighting and proper formatting. If Pygments is not installed, the field will be displayed without any formatting. Note that the absence of Pygments will not cause any errors in Unfold's functionality.

## Basic formatting without Pygments

Even without the Pygments library installed, you can still achieve basic JSON formatting by using the `PrettyJSONEncoder` encoder shown in the example below.

```python
# encoders.py

import json


class PrettyJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=4, sort_keys=True, **kwargs)
```

After creating the encoder, we can apply it to a field definition in the `models.py` file. When a value is saved to the database, this encoder will automatically format the JSON data. As a result, the raw value stored in the database will be properly formatted.

```python
# models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomModel(models.Model):
    data = models.JSONField(_("data"), null=True, blank=True, encoder=PrettyJSONEncoder)
```

Finally, register the model in admin.py and include the JSON field in the `readonly_fields` list to ensure it displays with proper formatting.

```python
# admin.py

from django.contrib import admin
from unfold.admin import ModelAdmin


@admin.register(CustomModel)
class CustomAdminClass(ModelAdmin):
    readonly_fields = ["data"]
```
