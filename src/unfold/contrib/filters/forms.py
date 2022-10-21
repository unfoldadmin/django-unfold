from django import forms
from django.utils.translation import gettext_lazy as _

from ...widgets import INPUT_CLASSES


class SingleNumericForm(forms.Form):
    def __init__(self, *args, **kwargs):
        name = kwargs.pop("name")
        super().__init__(*args, **kwargs)

        self.fields[name] = forms.FloatField(
            label="",
            required=False,
            widget=forms.NumberInput(
                attrs={"placeholder": _("Value"), "class": " ".join(INPUT_CLASSES)}
            ),
        )


class RangeNumericForm(forms.Form):
    name = None

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop("name")
        super().__init__(*args, **kwargs)

        self.fields[self.name + "_from"] = forms.FloatField(
            label="",
            required=False,
            widget=forms.NumberInput(
                attrs={"placeholder": _("From"), "class": " ".join(INPUT_CLASSES)}
            ),
        )
        self.fields[self.name + "_to"] = forms.FloatField(
            label="",
            required=False,
            widget=forms.NumberInput(
                attrs={"placeholder": _("To"), "class": " ".join(INPUT_CLASSES)}
            ),
        )


class SliderNumericForm(RangeNumericForm):
    pass
