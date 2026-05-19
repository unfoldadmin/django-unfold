from typing import Any

from crispy_forms.layout import BaseInput, LayoutObject
from crispy_forms.utils import TEMPLATE_PACK
from django.forms import Form
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.functional import SimpleLazyObject

from unfold.widgets import BUTTON_CLASSES


class ButtonClassesMixin:
    def __init__(self, *args: Any, css_class: str | None = None, **kwargs: Any) -> None:
        classes = BUTTON_CLASSES.copy()

        if css_class:
            classes.append(css_class)

        self.field_classes = " ".join(classes)

        super().__init__(*args, **kwargs)


class Submit(ButtonClassesMixin, BaseInput):
    input_type = "submit"


class Button(ButtonClassesMixin, BaseInput):
    input_type = "button"


class FieldsetSubheader(LayoutObject):
    template = "unfold_crispy/layout/fieldset_subheader.html"

    def __init__(self, title: str | None = None, *args: Any, **kwargs: Any) -> None:
        self.title = title
        super().__init__(*args, **kwargs)

    def render(
        self,
        form: Form,
        context: RequestContext,
        template_pack: SimpleLazyObject = TEMPLATE_PACK,
        **kwargs: Any,
    ) -> str:
        return render_to_string(
            self.template,
            {
                "title": self.title,
            },
        )


class Hr(LayoutObject):
    template = "unfold_crispy/layout/hr.html"

    def __init__(self, title: str | None = None, *args: Any, **kwargs: Any) -> None:
        self.title = title
        super().__init__(*args, **kwargs)

    def render(
        self,
        form: Form,
        context: RequestContext,
        template_pack: SimpleLazyObject = TEMPLATE_PACK,
        **kwargs: Any,
    ) -> str:
        return render_to_string(
            self.template,
            {
                "title": self.title,
            },
        )
