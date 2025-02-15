---
title: JsonField
order: 0
description: JsonField display options in Unfold
---

# JsonField formatting and syntax highlighting

At the moment, Unfold provides some basic JSON formatting and syntax highlighting but only in case the JSON field is in admin configuration in `readonly_fields` list. Otherwise, the field is displayed as plain text by using `UnfoldAdminTextareaWidget`.

Once the JSON field is in `readonly_fields` and at the same time Pygments library is installed (`pip install pygments`), the field is displayed with syntax highlighting and formatting. If Pygments is not installed, the field is displayed without formatting as it is. If the library is not available, Unfold will NOT throw any errors.

## Basic formatting without Pygments

Without the Pygments library, it is still possible to add at least some basic formatting to the JSON field by using example `PrettyJSONEncoder` encoder below.
```python
# encoders.py

import json


class PrettyJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=4, sort_keys=True, **kwargs)
```

Once we have this encoder, we will use it in the field definition in the `models.py` file. This encoder will format JSON when the field value is saved to the database so if you check the raw value in the database, it will be formatted.

```python
# models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomModel(models.Model):
    data = models.JSONField(_("data"), null=True, blank=True, encoder=PrettyJSONEncoder)
```

Again, we need to register the model in the admin.py file and make sure the new JSON field is in `readonly_fields` list to make sure it will be display with formatted content.

```python
# admin.py

from django.contrib import admin
from unfold.admin import ModelAdmin


@admin.register(CustomModel)
class CustomAdminClass(ModelAdmin):
    readonly_fields = ["data"]
```
