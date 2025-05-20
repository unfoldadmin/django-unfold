from typing import Any, Optional, Union

from django.core.validators import EMPTY_VALUES
from django.forms import MultiWidget, Widget
from django.http import QueryDict
from django.utils.datastructures import MultiValueDict

from unfold.widgets import (
    PROSE_CLASSES,
    UnfoldAdminSelectWidget,
    UnfoldAdminTextInputWidget,
)

WYSIWYG_CLASSES = [
    *PROSE_CLASSES,
    "border!",
    "border-base-200!",
    "border-t-0!",
    "group-[.errors]:border-red-600",
    "max-w-none",
    "p-4",
    "rounded-b",
    "rounded-t-none",
    "text-base-500",
    "w-full",
    "focus:outline-hidden",
    "dark:border-base-700!",
    "dark:text-base-300!",
    "dark:group-[.errors]:border-red-500!",
]


class ArrayWidget(MultiWidget):
    template_name = "unfold/forms/array.html"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if "choices" in kwargs:
            self.choices = kwargs["choices"]

        widgets = [self.get_widget_instance()]
        super().__init__(widgets)

    def get_widget_instance(self) -> Any:
        if hasattr(self, "choices"):
            return UnfoldAdminSelectWidget(choices=self.choices)

        return UnfoldAdminTextInputWidget()

    def get_context(self, name: str, value: str, attrs: dict) -> dict:
        self._resolve_widgets(value)
        context = super().get_context(name, value, attrs)
        context.update(
            {"template": self.get_widget_instance().get_context(name, "", {})["widget"]}
        )
        return context

    def value_from_datadict(
        self, data: QueryDict, files: MultiValueDict, name: str
    ) -> list:
        values = []

        for item in data.getlist(name):
            if item not in EMPTY_VALUES:
                values.append(item)

        return values

    def value_omitted_from_data(
        self, data: QueryDict, files: MultiValueDict, name: str
    ) -> list:
        return data.getlist(name) not in [[""], *EMPTY_VALUES]

    def decompress(self, value: Union[str, list]) -> list:
        if isinstance(value, list):
            return value
        elif isinstance(value, str):
            return value.split(",")

        return []

    def _resolve_widgets(self, value: Optional[Union[list, str]]) -> None:
        if value is None:
            value = []

        elif isinstance(value, list):
            self.widgets = [self.get_widget_instance() for item in value]
        else:
            self.widgets = [self.get_widget_instance() for item in value.split(",")]

        self.widgets_names = ["" for i in range(len(self.widgets))]
        self.widgets = [w if isinstance(w, type) else w for w in self.widgets]


class WysiwygWidget(Widget):
    template_name = "unfold/forms/wysiwyg.html"

    class Media:
        css = {"all": ("unfold/forms/css/trix/trix.css",)}
        js = (
            "unfold/forms/js/trix/trix.js",
            "unfold/forms/js/trix.config.js",
        )

    def __init__(self, attrs: Optional[dict[str, Any]] = None) -> None:
        super().__init__(attrs)

        self.attrs.update(
            {
                "class": " ".join(WYSIWYG_CLASSES),
            }
        )
