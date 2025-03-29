from django import forms
from django.contrib.admin.options import HORIZONTAL
from django.contrib.admin.widgets import AutocompleteSelect, AutocompleteSelectMultiple
from django.db.models import Field as ModelField
from django.forms import (
    ChoiceField,
    ModelMultipleChoiceField,
    MultipleChoiceField,
)
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
from unfold.widgets import (
    INPUT_CLASSES,
    UnfoldAdminCheckboxSelectMultiple,
    UnfoldAdminRadioSelectWidget,
    UnfoldAdminSelectMultipleWidget,
    UnfoldAdminSelectWidget,
    UnfoldAdminSplitDateTimeVerticalWidget,
    UnfoldAdminTextInputWidget,
)


class SearchForm(forms.Form):
    def __init__(self, name: str, label: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields[name] = forms.CharField(
            label=label,
            required=False,
            widget=UnfoldAdminTextInputWidget,
        )


class AutocompleteDropdownForm(forms.Form):
    field = forms.ModelChoiceField
    widget = AutocompleteSelect

    def __init__(
        self,
        request: HttpRequest,
        name: str,
        label: str,
        choices: tuple,
        field: ModelField,
        model_admin: ModelAdmin,
        multiple: bool = False,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        if multiple:
            self.field = ModelMultipleChoiceField
            self.widget = AutocompleteSelectMultiple

        self.fields[name] = self.field(
            label=label,
            required=False,
            queryset=field.remote_field.model.objects,
            widget=self.widget(field, model_admin.admin_site),
        )

    class Media:
        js = (
            "admin/js/vendor/jquery/jquery.js",
            "admin/js/vendor/select2/select2.full.js",
            "admin/js/jquery.init.js",
            "unfold/js/select2.init.js",
        )
        css = {
            "screen": (
                "admin/css/vendor/select2/select2.css",
                "admin/css/autocomplete.css",
            ),
        }


class CheckboxForm(forms.Form):
    field = MultipleChoiceField
    widget = UnfoldAdminCheckboxSelectMultiple

    def __init__(
        self,
        name: str,
        label: str,
        choices: tuple,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.fields[name] = self.field(
            label=label,
            required=False,
            choices=choices,
            widget=self.widget,
        )


class RadioForm(CheckboxForm):
    field = ChoiceField
    widget = UnfoldAdminRadioSelectWidget


class HorizontalRadioForm(RadioForm):
    horizontal = True
    widget = UnfoldAdminRadioSelectWidget(radio_style=HORIZONTAL)


class DropdownForm(forms.Form):
    widget = UnfoldAdminSelectWidget(
        attrs={
            "data-theme": "admin-autocomplete",
            "class": "unfold-admin-autocomplete admin-autocomplete",
        }
    )
    field = ChoiceField

    def __init__(
        self,
        name: str,
        label: str,
        choices: tuple,
        multiple: bool = False,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        if multiple:
            self.widget = UnfoldAdminSelectMultipleWidget(
                attrs={
                    "data-theme": "admin-autocomplete",
                    "class": "unfold-admin-autocomplete admin-autocomplete",
                }
            )
            self.field = MultipleChoiceField

        self.fields[name] = self.field(
            label=label,
            required=False,
            choices=choices,
            widget=self.widget,
        )

    class Media:
        js = (
            "admin/js/vendor/jquery/jquery.js",
            "admin/js/vendor/select2/select2.full.js",
            "admin/js/jquery.init.js",
            "unfold/js/select2.init.js",
        )
        css = {
            "screen": (
                "admin/css/vendor/select2/select2.css",
                "admin/css/autocomplete.css",
            ),
        }


class SingleNumericForm(forms.Form):
    def __init__(self, name: str, *args, **kwargs) -> None:
        self.name = name
        super().__init__(*args, **kwargs)

        self.fields[name] = forms.FloatField(
            label="",
            required=False,
            widget=forms.NumberInput(
                attrs={"placeholder": _("Value"), "class": " ".join(INPUT_CLASSES)}
            ),
        )


class RangeNumericForm(forms.Form):
    def __init__(self, name: str, *args, **kwargs) -> None:
        self.name = name
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
    class Media:
        css = {"all": ("unfold/filters/css/nouislider.min.css",)}
        js = (
            "unfold/filters/js/wNumb.min.js",
            "unfold/filters/js/nouislider.min.js",
            "unfold/filters/js/admin-numeric-filter.js",
        )


class RangeDateForm(forms.Form):
    class Media:
        js = [
            "admin/js/calendar.js",
            "unfold/filters/js/DateTimeShortcuts.js",
        ]

    def __init__(self, name: str, *args, **kwargs) -> None:
        self.name = name
        super().__init__(*args, **kwargs)

        self.fields[self.name + "_from"] = forms.DateField(
            label="",
            required=False,
            widget=forms.DateInput(
                attrs={
                    "placeholder": _("From"),
                    "class": "vCustomDateField " + " ".join(INPUT_CLASSES),
                }
            ),
        )
        self.fields[self.name + "_to"] = forms.DateField(
            label="",
            required=False,
            widget=forms.DateInput(
                attrs={
                    "placeholder": _("To"),
                    "class": "vCustomDateField " + " ".join(INPUT_CLASSES),
                }
            ),
        )


class RangeDateTimeForm(forms.Form):
    class Media:
        js = [
            "admin/js/calendar.js",
            "unfold/filters/js/DateTimeShortcuts.js",
        ]

    def __init__(self, name: str, *args, **kwargs) -> None:
        self.name = name
        super().__init__(*args, **kwargs)

        self.fields[self.name + "_from"] = forms.SplitDateTimeField(
            label="",
            required=False,
            widget=UnfoldAdminSplitDateTimeVerticalWidget(
                date_label="",
                date_attrs={
                    "placeholder": _("Date from"),
                    "class": "vCustomDateField " + " ".join(INPUT_CLASSES),
                },
                time_label="",
                time_attrs={
                    "placeholder": _("Time"),
                    "class": "vCustomTimeField " + " ".join(INPUT_CLASSES),
                },
            ),
        )
        self.fields[self.name + "_to"] = forms.SplitDateTimeField(
            label="",
            required=False,
            widget=UnfoldAdminSplitDateTimeVerticalWidget(
                date_label="",
                date_attrs={
                    "placeholder": _("Date to"),
                    "class": "vCustomDateField " + " ".join(INPUT_CLASSES),
                },
                time_label="",
                time_attrs={
                    "placeholder": _("Time"),
                    "class": "vCustomTimeField " + " ".join(INPUT_CLASSES),
                },
            ),
        )
