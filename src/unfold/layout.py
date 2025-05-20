from crispy_forms.layout import BaseInput, LayoutObject
from crispy_forms.utils import TEMPLATE_PACK
from django.template.loader import render_to_string

from unfold.widgets import BUTTON_CLASSES


class ButtonClassesMixin:
    def __init__(self, *args, css_class=None, **kwargs):
        classes = BUTTON_CLASSES

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

    def __init__(self, title=None, *args, **kwargs):
        self.title = title
        super().__init__(*args, **kwargs)

    def render(self, form, context, template_pack=TEMPLATE_PACK, **kwargs):
        return render_to_string(
            self.template,
            {
                "title": self.title,
            },
        )


class Hr(LayoutObject):
    template = "unfold_crispy/layout/hr.html"

    def __init__(self, title=None, *args, **kwargs):
        self.title = title
        super().__init__(*args, **kwargs)

    def render(self, form, context, template_pack=TEMPLATE_PACK, **kwargs):
        return render_to_string(
            self.template,
            {
                "title": self.title,
            },
        )
