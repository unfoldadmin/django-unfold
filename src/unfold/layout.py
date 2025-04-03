from crispy_forms.layout import BaseInput

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
