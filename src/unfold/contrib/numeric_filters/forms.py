from django import forms
from django.utils.translation import ugettext_lazy as _


class SingleNumericForm(forms.Form):
    def __init__(self, *args, **kwargs):
        name = kwargs.pop("name")
        super().__init__(*args, **kwargs)

        self.fields[name] = forms.FloatField(
            label="",
            required=False,
            widget=forms.NumberInput(
                attrs={
                    "placeholder": _("Value"),
                    "class": "border bg-white font-medium mb-2 px-3 py-2 rounded-md shadow-sm text-gray-500 text-sm \
                    w-full focus:ring focus:ring-primary-300 focus:border-primary-600 focus:outline-none",
                }
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
                attrs={
                    "placeholder": _("From"),
                    "class": "border bg-white font-medium px-3 py-2 rounded-md shadow-sm text-gray-500 text-sm w-full \
                    focus:ring focus:ring-primary-300 focus:border-primary-600 focus:outline-none",
                }
            ),
        )
        self.fields[self.name + "_to"] = forms.FloatField(
            label="",
            required=False,
            widget=forms.NumberInput(
                attrs={
                    "placeholder": _("To"),
                    "class": "border bg-white font-medium my-2 px-3 py-2 rounded-md shadow-sm text-gray-500 text-sm \
                    w-full focus:ring focus:ring-primary-300 focus:border-primary-600 focus:outline-none",
                }
            ),
        )


class SliderNumericForm(RangeNumericForm):
    pass
