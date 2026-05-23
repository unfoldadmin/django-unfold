from typing import Any

from django.db import models

from unfold.fields import UnfoldAdminJSONSchemaField


class JSONSchemaField(models.JSONField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.schema = kwargs.pop("schema", {})
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs: Any) -> UnfoldAdminJSONSchemaField:
        defaults = {
            "form_class": UnfoldAdminJSONSchemaField,
            "schema": self.schema,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
