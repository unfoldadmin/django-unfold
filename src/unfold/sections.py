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
        results = getattr(self.instance, self.related_name)
        headers = []
        rows = []

        for model_field in results.model._meta.fields:
            for field in self.fields:
                if field == "pk":
                    field = "id"

                if model_field.name == field:
                    headers.append(model_field.verbose_name)

        for result in results.all():
            row = []

            for field in self.fields:
                row.append(display_for_field(getattr(result, field), field, "-"))

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

    def render(self) -> str:
        return render_to_string(
            self.template_name,
            context={
                "request": self.request,
                "instance": self.instance,
            },
        )
