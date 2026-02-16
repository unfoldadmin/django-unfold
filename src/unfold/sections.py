from typing import Any

from django.contrib.admin.utils import label_for_field, lookup_field
from django.db.models import Model
from django.http import HttpRequest
from django.template.loader import render_to_string

from unfold.utils import display_for_field


class BaseSection:
    def __init__(self, request: HttpRequest, instance: Model) -> None:
        self.request = request
        self.instance = instance

    def render(self) -> str:
        raise NotImplementedError(
            "Section subclasses must implement the render method."
        )


class TableSection(BaseSection):
    fields = []
    related_name = None
    verbose_name = None
    height = None

    def render(self) -> str:
        if self.related_name is None:
            raise ValueError("TableSection must have a related_name")

        results = getattr(self.instance, self.related_name)
        headers = []
        rows = []

        for field_name in self.fields:
            if hasattr(self, field_name):
                if hasattr(getattr(self, field_name), "short_description"):
                    headers.append(getattr(self, field_name).short_description)
                else:
                    headers.append(field_name)
            else:
                headers.append(label_for_field(field_name, results.model))

        for result in results.all():
            row = []

            for field_name in self.fields:
                if hasattr(self, field_name):
                    row.append(getattr(self, field_name)(result))
                else:
                    field, attr, value = lookup_field(field_name, result)
                    row.append(display_for_field(value, field, "-"))

            rows.append(row)

        context = {
            "request": self.request,
            "table": {
                "headers": headers,
                "rows": rows,
            },
        }

        if hasattr(self, "verbose_name") and self.verbose_name:
            context["title"] = self.verbose_name

        if hasattr(self, "height") and self.height:
            context["height"] = self.height

        return render_to_string(
            "unfold/components/table.html",
            context=context,
        )


class TemplateSection(BaseSection):
    template_name = None

    def get_context_data(self, request: HttpRequest, instance: Model) -> dict[str, Any]:
        return {}

    def render(self) -> str:
        if self.template_name is None:
            raise ValueError("TemplateSection must have a template_name")

        return render_to_string(
            self.template_name,
            context={
                **self.get_context_data(self.request, self.instance),
                "request": self.request,
                "instance": self.instance,
            },
        )
