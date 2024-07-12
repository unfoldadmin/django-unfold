from typing import Any, Dict, List, Optional, Union

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
    "border",
    "border-gray-200",
    "border-t-0",
    "group-[.errors]:border-red-600",
    "max-w-none",
    "p-4",
    "rounded-b-md",
    "rounded-t-none",
    "text-gray-500",
    "w-full",
    "focus:outline-none",
    "dark:border-gray-700",
    "dark:text-gray-300",
    "dark:group-[.errors]:border-red-500",
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

    def get_context(self, name: str, value: str, attrs: Dict) -> Dict:
        self._resolve_widgets(value)
        context = super().get_context(name, value, attrs)
        context.update(
            {"template": self.get_widget_instance().get_context(name, "", {})["widget"]}
        )
        return context

    def value_from_datadict(
        self, data: QueryDict, files: MultiValueDict, name: str
    ) -> List:
        values = []

        for item in data.getlist(name):
            if item not in EMPTY_VALUES:
                values.append(item)

        return values

    def value_omitted_from_data(
        self, data: QueryDict, files: MultiValueDict, name: str
    ) -> List:
        return data.getlist(name) not in [[""], *EMPTY_VALUES]

    def decompress(self, value: Union[str, List]) -> List:
        if isinstance(value, List):
            return value
        elif isinstance(value, str):
            return value.split(",")

        return []

    def _resolve_widgets(self, value: Optional[Union[List, str]]) -> None:
        if value is None:
            value = []

        elif isinstance(value, List):
            self.widgets = [self.get_widget_instance() for item in value]
        else:
            self.widgets = [self.get_widget_instance() for item in value.split(",")]

        self.widgets_names = ["" for i in range(len(self.widgets))]
        self.widgets = [w if isinstance(w, type) else w for w in self.widgets]


class WysiwygWidget(Widget):
    template_name = "unfold/forms/wysiwyg.html"

    class Media:
        css = {"all": ("unfold/forms/css/trix.css",)}
        js = (
            "unfold/forms/js/trix.js",
            "unfold/forms/js/trix.config.js",
        )

    def __init__(self, attrs: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(attrs)

        self.attrs.update(
            {
                "class": " ".join(WYSIWYG_CLASSES),
            }
        )
