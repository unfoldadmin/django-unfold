from typing import Any, Dict, Optional

from django.forms import Widget
from unfold.widgets import PROSE_CLASSES

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
    "dark:text-gray-400",
    "dark:group-[.errors]:border-red-500",
]


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
