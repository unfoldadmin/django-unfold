from typing import Any

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Model

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

    def validate(self, value: Any, model_instance: Model | None) -> None:
        super().validate(value, model_instance)

        if not self.schema:
            return

        try:
            import jsonschema
        except ImportError:
            return

        try:
            jsonschema.validate(value, self.schema)
        except jsonschema.ValidationError as e:
            paths = ", ".join(str(p) for p in e.path)
            raise ValidationError(f"{paths}: {e.message}") from e
