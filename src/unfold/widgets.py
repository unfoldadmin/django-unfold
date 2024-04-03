from typing import Any, Callable, Dict, Optional, Tuple, Union

from django.contrib.admin.options import VERTICAL
from django.contrib.admin.widgets import (
    AdminBigIntegerFieldWidget,
    AdminDateWidget,
    AdminEmailInputWidget,
    AdminFileWidget,
    AdminIntegerFieldWidget,
    AdminRadioSelect,
    AdminSplitDateTime,
    AdminTextareaWidget,
    AdminTextInputWidget,
    AdminTimeWidget,
    AdminUUIDInputWidget,
)
from django.forms import (
    CheckboxInput,
    MultiWidget,
    NullBooleanSelect,
    NumberInput,
    Select,
)
from django.utils.translation import gettext_lazy as _

from .exceptions import UnfoldException
from .settings import get_config


class UnfoldAdminTextInputWidget(AdminTextInputWidget):
    def __init__(self, attrs: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            attrs={"class": " ".join(get_config()["INPUT_CLASSES"]), **(attrs or {})}
        )


class UnfoldAdminColorInputWidget(AdminTextInputWidget):
    def __init__(self, attrs: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            attrs={
                "type": "color",
                "class": " ".join(get_config()["COLOR_CLASSES"]),
                **(attrs or {}),
            }
        )


class UnfoldAdminUUIDInputWidget(AdminUUIDInputWidget):
    def __init__(self, attrs: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            attrs={"class": " ".join(get_config()["INPUT_CLASSES"]), **(attrs or {})}
        )


class UnfoldAdminIntegerRangeWidget(MultiWidget):
    template_name = "unfold/widgets/range.html"

    def __init__(self, attrs: Optional[Dict[str, Any]] = None) -> None:
        if attrs is None:
            attrs = {}

        attrs["class"] = " ".join(get_config()["INPUT_CLASSES"])

        _widgets = (NumberInput(attrs=attrs), NumberInput(attrs=attrs))

        super().__init__(_widgets, attrs)

    def decompress(self, value: Union[str, None]) -> Tuple[Optional[Callable], ...]:
        if value:
            return value.lower, value.upper
        return None, None


class UnfoldAdminEmailInputWidget(AdminEmailInputWidget):
    def __init__(self, attrs: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            attrs={"class": " ".join(get_config()["INPUT_CLASSES"]), **(attrs or {})}
        )


class FileFieldMixin:
    def get_context(self, name, value, attrs):
        widget = super().get_context(name, value, attrs)
        widget["widget"].update(
            {
                "class": " ".join(
                    [*get_config()["CHECKBOX_CLASSES"], *["form-check-input"]]
                )
            }
        )
        return widget


class UnfoldAdminImageFieldWidget(FileFieldMixin, AdminFileWidget):
    pass


class UnfoldAdminFileFieldWidget(FileFieldMixin, AdminFileWidget):
    template_name = "unfold/widgets/clearable_file_input_small.html"


class UnfoldAdminImageSmallFieldWidget(FileFieldMixin, AdminFileWidget):
    template_name = "unfold/widgets/clearable_file_input_small.html"


class UnfoldAdminDateWidget(AdminDateWidget):
    def __init__(
        self, attrs: Optional[Dict[str, Any]] = None, format: Optional[str] = None
    ) -> None:
        attrs = {
            "class": "vDateField " + " ".join(get_config()["INPUT_CLASSES"]),
            "size": "10",
            **(attrs or {}),
        }
        super().__init__(attrs=attrs, format=format)


class UnfoldAdminSingleDateWidget(AdminDateWidget):
    template_name = "unfold/widgets/date.html"

    def __init__(
        self, attrs: Optional[Dict[str, Any]] = None, format: Optional[str] = None
    ) -> None:
        attrs = {
            "class": "vDateField " + " ".join(get_config()["INPUT_CLASSES"]),
            "size": "10",
            **(attrs or {}),
        }
        super().__init__(attrs=attrs, format=format)


class UnfoldAdminTimeWidget(AdminTimeWidget):
    def __init__(
        self, attrs: Optional[Dict[str, Any]] = None, format: Optional[str] = None
    ) -> None:
        attrs = {
            "class": "vTimeField " + " ".join(get_config()["INPUT_CLASSES"]),
            "size": "8",
            **(attrs or {}),
        }
        super().__init__(attrs=attrs, format=format)


class UnfoldAdminSingleTimeWidget(AdminTimeWidget):
    template_name = "unfold/widgets/time.html"

    def __init__(
        self, attrs: Optional[Dict[str, Any]] = None, format: Optional[str] = None
    ) -> None:
        attrs = {
            "class": "vTimeField " + " ".join(get_config()["INPUT_CLASSES"]),
            "size": "8",
            **(attrs or {}),
        }
        super().__init__(attrs=attrs, format=format)


class UnfoldAdminTextareaWidget(AdminTextareaWidget):
    template_name = "unfold/widgets/textarea.html"

    def __init__(self, attrs: Optional[Dict[str, Any]] = None) -> None:
        attrs = attrs or {}

        attrs.update({"rows": 2})

        super().__init__(
            attrs={
                "class": "vLargeTextField "
                + " ".join(get_config()["TEXTAREA_CLASSES"])
                + " "
                + " ".join(get_config()["TEXTAREA_EXPANDABLE_CLASSES"]),
                **(attrs or {}),
            }
        )


class UnfoldAdminSplitDateTimeWidget(AdminSplitDateTime):
    def __init__(self, attrs: Optional[Dict[str, Any]] = None) -> None:
        widgets = [UnfoldAdminDateWidget, UnfoldAdminTimeWidget]
        MultiWidget.__init__(self, widgets, attrs)


class UnfoldAdminSplitDateTimeVerticalWidget(AdminSplitDateTime):
    template_name = "unfold/widgets/split_datetime_vertical.html"

    def __init__(
        self,
        attrs: Optional[Dict[str, Any]] = None,
        date_attrs: Optional[Dict[str, Any]] = None,
        time_attrs: Optional[Dict[str, Any]] = None,
        date_label: Optional[str] = None,
        time_label: Optional[str] = None,
    ) -> None:
        self.date_label = date_label
        self.time_label = time_label

        widgets = [
            UnfoldAdminDateWidget(attrs=date_attrs),
            UnfoldAdminTimeWidget(attrs=time_attrs),
        ]
        MultiWidget.__init__(self, widgets, attrs)

    def get_context(
        self, name: str, value: Any, attrs: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        context = super().get_context(name, value, attrs)

        if self.date_label is not None:
            context["date_label"] = self.date_label
        else:
            context["date_label"] = _("Date")

        if self.time_label is not None:
            context["time_label"] = self.time_label
        else:
            context["time_label"] = _("Time")

        return context


class UnfoldAdminIntegerFieldWidget(AdminIntegerFieldWidget):
    def __init__(self, attrs: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            attrs={"class": " ".join(get_config()["INPUT_CLASSES"]), **(attrs or {})}
        )


class UnfoldAdminDecimalFieldWidget(AdminIntegerFieldWidget):
    def __init__(self, attrs: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            attrs={"class": " ".join(get_config()["INPUT_CLASSES"]), **(attrs or {})}
        )


class UnfoldAdminBigIntegerFieldWidget(AdminBigIntegerFieldWidget):
    def __init__(self, attrs: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            attrs={"class": " ".join(get_config()["INPUT_CLASSES"]), **(attrs or {})}
        )


class UnfoldAdminNullBooleanSelectWidget(NullBooleanSelect):
    pass


class UnfoldAdminSelect(Select):
    def __init__(self, attrs=None, choices=()):
        if attrs is None:
            attrs = {}

        attrs["class"] = " ".join(get_config()["SELECT_CLASSES"])
        super().__init__(attrs, choices)


class UnfoldAdminRadioSelectWidget(AdminRadioSelect):
    option_template_name = "admin/widgets/radio_option.html"

    def __init__(self, radio_style: Optional[int] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if radio_style is None:
            radio_style = VERTICAL

        self.radio_style = radio_style
        self.attrs = {"class": " ".join(get_config()["RADIO_CLASSES"])}

    def get_context(self, *args, **kwargs) -> Dict[str, Any]:
        context = super().get_context(*args, **kwargs)
        context.update({"radio_style": self.radio_style})
        return context


try:
    from djmoney.forms.widgets import MoneyWidget
    from djmoney.settings import CURRENCY_CHOICES

    class UnfoldAdminMoneyWidget(MoneyWidget):
        template_name = "unfold/widgets/split_money.html"

        def __init__(self, *args, **kwargs):
            super().__init__(
                amount_widget=UnfoldAdminTextInputWidget,
                currency_widget=UnfoldAdminSelect(choices=CURRENCY_CHOICES),
            )

except ImportError:

    class UnfoldAdminMoneyWidget:
        def __init__(self, *args, **kwargs):
            raise UnfoldException("django-money not installed")


class UnfoldBooleanWidget(CheckboxInput):
    def __init__(
        self, attrs: Optional[Dict[str, Any]] = None, check_test: Callable = None
    ) -> None:
        if attrs is None:
            attrs = {}

        return super().__init__(
            {
                **(attrs or {}),
                "class": " ".join(
                    get_config()["CHECKBOX_CLASSES"] + [attrs.get("class", "")]
                ),
            },
            check_test,
        )


class UnfoldBooleanSwitchWidget(CheckboxInput):
    def __init__(
        self, attrs: Optional[Dict[str, Any]] = None, check_test: Callable = None
    ) -> None:
        return super().__init__(
            attrs={"class": " ".join(get_config()["SWITCH_CLASSES"]), **(attrs or {})},
            check_test=None,
        )
