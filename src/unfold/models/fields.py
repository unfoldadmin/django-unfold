from typing import Any

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Model
from django.utils.module_loading import import_string

from unfold.fields import UnfoldAdminJSONSchemaField


class JSONSchemaField(models.JSONField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        schema = kwargs.pop("schema", {})

        if isinstance(schema, str):
            try:
                schema_obj = import_string(schema)

                if not callable(schema_obj):
                    raise TypeError(
                        f"The imported schema object from '{schema}' must be callable."
                    )

                self.schema = schema_obj()
            except Exception as exc:
                raise ImportError(
                    f"Could not import callable schema from dotted path '{schema}': {exc}"
                ) from exc
        else:
            self.schema = schema

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
