from typing import Any, Callable, Optional, Union

from django.contrib.admin.options import VERTICAL
from django.contrib.admin.sites import AdminSite
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
    AdminURLFieldWidget,
    AdminUUIDInputWidget,
    ForeignKeyRawIdWidget,
    RelatedFieldWidgetWrapper,
)
from django.db.models.fields.reverse_related import ForeignObjectRel
from django.forms import (
    CheckboxInput,
    CheckboxSelectMultiple,
    MultiWidget,
    NullBooleanSelect,
    NumberInput,
    PasswordInput,
    Select,
    SelectMultiple,
)
from django.utils.translation import gettext_lazy as _

from .exceptions import UnfoldException

BUTTON_CLASSES = [
    "border",
    "cursor-pointer",
    "font-medium",
    "px-3",
    "py-2",
    "rounded",
    "text-center",
    "whitespace-nowrap",
    "bg-primary-600",
    "border-transparent",
    "text-white",
]

LABEL_CLASSES = [
    "block",
    "font-semibold",
    "mb-2",
    "text-font-important-light",
    "text-sm",
    "dark:text-font-important-dark",
]

CHECKBOX_LABEL_CLASSES = [
    "font-semibold",
    "ml-2",
    "text-sm",
    "text-font-important-light",
    "dark:text-font-important-dark",
]

BASE_CLASSES = [
    "border",
    "border-base-200",
    "bg-white",
    "font-medium",
    "min-w-20",
    "placeholder-base-400",
    "rounded",
    "shadow-sm",
    "text-font-default-light",
    "text-sm",
    "focus:ring",
    "focus:ring-primary-300",
    "focus:border-primary-600",
    "focus:outline-none",
    "group-[.errors]:border-red-600",
    "group-[.errors]:focus:ring-red-200",
    "dark:bg-base-900",
    "dark:border-base-700",
    "dark:text-font-default-dark",
    "dark:focus:border-primary-600",
    "dark:focus:ring-primary-700",
    "dark:focus:ring-opacity-50",
    "dark:group-[.errors]:border-red-500",
    "dark:group-[.errors]:focus:ring-red-600/40",
]

BASE_INPUT_CLASSES = [
    *BASE_CLASSES,
    "px-3",
    "py-2",
    "w-full",
]

INPUT_CLASSES = [*BASE_INPUT_CLASSES, "max-w-2xl"]

DATETIME_CLASSES = [*BASE_INPUT_CLASSES, "min-w-52"]

COLOR_CLASSES = [*BASE_CLASSES, "h-9.5", "px-2", "py-2", "w-32"]

INPUT_CLASSES_READONLY = [*BASE_INPUT_CLASSES, "bg-base-50"]

TEXTAREA_CLASSES = [
    *BASE_INPUT_CLASSES,
    "max-w-4xl",
    "appearance-none",
    "expandable",
    "transition",
    "transition-height",
    "duration-75",
    "ease-in-out",
]

TEXTAREA_EXPANDABLE_CLASSES = [
    "block",
    "field-sizing-content",
    "min-h-[38px]",
]

SELECT_CLASSES = [
    *BASE_INPUT_CLASSES,
    "pr-8",
    "max-w-2xl",
    "appearance-none",
]

PROSE_CLASSES = [
    "font-normal",
    "whitespace-normal",
    "prose-sm",
    "prose-blockquote:border-l-4",
    "prose-blockquote:not-italic",
    "prose-pre:bg-base-50",
    "prose-pre:rounded",
    "prose-headings:font-medium",
    "prose-a:text-primary-600",
    "prose-headings:font-medium",
    "prose-headings:text-base-700",
    "prose-ol:list-decimal",
    "prose-ul:list-disc",
    "prose-strong:text-base-700",
    "dark:prose-pre:bg-base-800",
    "dark:prose-blockquote:border-base-700",
    "dark:prose-blockquote:text-base-300",
    "dark:prose-headings:text-base-200",
    "dark:prose-strong:text-base-200",
]

CHECKBOX_CLASSES = [
    "appearance-none",
    "bg-white",
    "block",
    "border",
    "border-base-300",
    "cursor-pointer",
    "h-4",
    "min-w-4",
    "relative",
    "rounded-[4px]",
    "shadow-sm",
    "w-4",
    "hover:border-base-400",
    "dark:bg-base-700",
    "dark:border-base-500",
    "dark:after:checked:text-white",
    "focus:outline",
    "focus:outline-1",
    "focus:outline-offset-2",
    "focus:outline-primary-500",
    "after:absolute",
    "after:content-['done']",
    "after:!flex",
    "after:h-4",
    "after:items-center",
    "after:justify-center",
    "after:leading-none",
    "after:material-symbols-outlined",
    "after:-ml-px",
    "after:-mt-px",
    "after:!text-sm",
    "after:text-white",
    "after:transition-all",
    "after:w-4",
    "after:dark:text-base-700",
    "checked:bg-primary-600",
    "checked:dark:bg-primary-600",
    "checked:border-primary-600",
    "checked:dark:border-primary-600",
    "checked:transition-all",
    "checked:hover:border-primary-600",
]

RADIO_CLASSES = [
    "appearance-none",
    "bg-white",
    "block",
    "border",
    "border-base-300",
    "cursor-pointer",
    "h-4",
    "min-w-4",
    "relative",
    "rounded-full",
    "w-4",
    "dark:bg-base-700",
    "dark:border-base-500",
    "hover:border-base-400",
    "focus:outline",
    "focus:outline-1",
    "focus:outline-offset-2",
    "focus:outline-primary-500",
    "after:absolute",
    "after:bg-transparent",
    "after:content-['']",
    "after:flex",
    "after:h-2",
    "after:items-center",
    "after:justify-center",
    "after:leading-none",
    "after:left-1/2",
    "after:rounded-full",
    "after:text-white",
    "after:top-1/2",
    "after:transition-all",
    "after:-translate-x-1/2",
    "after:-translate-y-1/2",
    "after:text-sm",
    "after:w-2",
    "after:dark:text-base-700",
    "after:dark:bg-transparent",
    "checked:bg-primary-600",
    "checked:border-primary-600",
    "checked:transition-all",
    "checked:after:bg-white",
    "checked:after:dark:bg-base-900",
    "checked:hover:border-base-900/20",
]

SWITCH_CLASSES = [
    "appearance-none",
    "bg-base-300",
    "cursor-pointer",
    "h-5",
    "relative",
    "rounded-full",
    "transition-all",
    "w-8",
    "min-w-8",
    "after:absolute",
    "after:bg-white",
    "after:content-['']",
    "after:bg-red-300",
    "after:h-3",
    "after:rounded-full",
    "after:shadow-sm",
    "after:left-1",
    "after:top-1",
    "after:w-3",
    "checked:bg-green-500",
    "checked:after:left-4",
    "dark:bg-base-600",
    "dark:checked:bg-green-700",
]

FILE_CLASSES = [
    "border",
    "border-base-200",
    "flex",
    "grow",
    "items-center",
    "overflow-hidden",
    "rounded",
    "shadow-sm",
    "max-w-2xl",
    "focus-within:ring",
    "group-[.errors]:border-red-600",
    "group-[.errors]:focus-within:ring-red-200",
    "focus-within:ring-primary-300",
    "focus-within:border-primary-600",
    "dark:border-base-700",
    "dark:focus-within:border-primary-600",
    "dark:focus-within:ring-primary-700",
    "dark:group-[.errors]:border-red-500",
    "dark:group-[.errors]:focus-within:ring-red-600/40",
]


class UnfoldAdminTextInputWidget(AdminTextInputWidget):
    def __init__(self, attrs: Optional[dict[str, Any]] = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            }
        )


class UnfoldAdminURLInputWidget(AdminURLFieldWidget):
    template_name = "unfold/widgets/url.html"

    def __init__(self, attrs: Optional[dict[str, Any]] = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            }
        )


class UnfoldAdminColorInputWidget(AdminTextInputWidget):
    def __init__(self, attrs: Optional[dict[str, Any]] = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "type": "color",
                "class": " ".join(
                    [*COLOR_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            }
        )


class UnfoldAdminUUIDInputWidget(AdminUUIDInputWidget):
    def __init__(self, attrs: Optional[dict[str, Any]] = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            }
        )


class UnfoldAdminIntegerRangeWidget(MultiWidget):
    template_name = "unfold/widgets/range.html"

    def __init__(self, attrs: Optional[dict[str, Any]] = None) -> None:
        if attrs is None:
            attrs = {}

        attrs["class"] = " ".join(
            [*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]
        )

        _widgets = (NumberInput(attrs=attrs), NumberInput(attrs=attrs))

        super().__init__(_widgets, attrs)

    def decompress(self, value: Union[str, None]) -> tuple[Optional[Callable], ...]:
        if value:
            return value.lower, value.upper
        return None, None


class UnfoldAdminEmailInputWidget(AdminEmailInputWidget):
    def __init__(self, attrs: Optional[dict[str, Any]] = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            }
        )


class FileFieldMixin:
    def get_context(self, name, value, attrs):
        widget = super().get_context(name, value, attrs)

        widget["widget"].update(
            {
                "class": " ".join([*CHECKBOX_CLASSES, *["form-check-input"]]),
                "file_wrapper_class": " ".join(FILE_CLASSES),
                "file_input_class": " ".join(
                    [
                        self.attrs.get("class", ""),
                        *[
                            "opacity-0",
                            "pointer-events-none",
                        ],
                    ]
                ),
            }
        )

        return widget


class UnfoldAdminImageFieldWidget(FileFieldMixin, AdminFileWidget):
    template_name = "unfold/widgets/clearable_file_input.html"


class UnfoldAdminFileFieldWidget(FileFieldMixin, AdminFileWidget):
    template_name = "unfold/widgets/clearable_file_input_small.html"


class UnfoldAdminImageSmallFieldWidget(FileFieldMixin, AdminFileWidget):
    template_name = "unfold/widgets/clearable_file_input_small.html"


class UnfoldAdminDateWidget(AdminDateWidget):
    template_name = "unfold/widgets/date.html"

    def __init__(
        self, attrs: Optional[dict[str, Any]] = None, format: Optional[str] = None
    ) -> None:
        attrs = {
            **(attrs or {}),
            "class": " ".join(
                [
                    "vDateField",
                    *DATETIME_CLASSES,
                    attrs.get("class", "") if attrs else "",
                ]
            ),
            "size": "10",
        }
        super().__init__(attrs=attrs, format=format)

    class Media:
        js = [
            "admin/js/core.js",
            "admin/js/calendar.js",
            "admin/js/admin/DateTimeShortcuts.js",
        ]


class UnfoldAdminSingleDateWidget(AdminDateWidget):
    template_name = "unfold/widgets/date.html"

    def __init__(
        self, attrs: Optional[dict[str, Any]] = None, format: Optional[str] = None
    ) -> None:
        attrs = {
            **(attrs or {}),
            "class": " ".join(
                [
                    "vDateField",
                    *DATETIME_CLASSES,
                    attrs.get("class", "") if attrs else "",
                ]
            ),
            "size": "10",
        }
        super().__init__(attrs=attrs, format=format)


class UnfoldAdminTimeWidget(AdminTimeWidget):
    template_name = "unfold/widgets/time.html"

    def __init__(
        self, attrs: Optional[dict[str, Any]] = None, format: Optional[str] = None
    ) -> None:
        attrs = {
            **(attrs or {}),
            "class": " ".join(
                [
                    "vTimeField",
                    *DATETIME_CLASSES,
                    attrs.get("class", "") if attrs else "",
                ]
            ),
            "size": "8",
        }
        super().__init__(attrs=attrs, format=format)

    class Media:
        js = [
            "admin/js/core.js",
            "admin/js/calendar.js",
            "admin/js/admin/DateTimeShortcuts.js",
        ]


class UnfoldAdminSingleTimeWidget(AdminTimeWidget):
    template_name = "unfold/widgets/time.html"

    def __init__(
        self, attrs: Optional[dict[str, Any]] = None, format: Optional[str] = None
    ) -> None:
        attrs = {
            **(attrs or {}),
            "class": " ".join(
                [
                    "vTimeField",
                    *DATETIME_CLASSES,
                    attrs.get("class", "") if attrs else "",
                ]
            ),
            "size": "8",
        }
        super().__init__(attrs=attrs, format=format)


class UnfoldAdminTextareaWidget(AdminTextareaWidget):
    template_name = "unfold/widgets/textarea.html"

    def __init__(self, attrs: Optional[dict[str, Any]] = None) -> None:
        attrs = attrs or {}

        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [
                        "vLargeTextField",
                        *TEXTAREA_CLASSES,
                        attrs.get("class", "") if attrs else "",
                    ]
                ),
            }
        )


class UnfoldAdminExpandableTextareaWidget(UnfoldAdminTextareaWidget):
    def __init__(self, attrs: Optional[dict[str, Any]] = None) -> None:
        attrs = attrs or {}

        attrs.update({"rows": 2})

        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [
                        "vLargeTextField",
                        *TEXTAREA_CLASSES,
                        *TEXTAREA_EXPANDABLE_CLASSES,
                        attrs.get("class", "") if attrs else "",
                    ]
                ),
            }
        )


class UnfoldAdminSplitDateTimeWidget(AdminSplitDateTime):
    template_name = "unfold/widgets/split_datetime.html"

    def __init__(self, attrs: Optional[dict[str, Any]] = None) -> None:
        widgets = [
            UnfoldAdminDateWidget(attrs={"placeholder": _("Date")}),
            UnfoldAdminTimeWidget(attrs={"placeholder": _("Time")}),
        ]
        MultiWidget.__init__(self, widgets, attrs)

    class Media:
        js = [
            "admin/js/core.js",
            "admin/js/calendar.js",
            "admin/js/admin/DateTimeShortcuts.js",
        ]


class UnfoldAdminSplitDateTimeVerticalWidget(AdminSplitDateTime):
    template_name = "unfold/widgets/split_datetime_vertical.html"

    def __init__(
        self,
        attrs: Optional[dict[str, Any]] = None,
        date_attrs: Optional[dict[str, Any]] = None,
        time_attrs: Optional[dict[str, Any]] = None,
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
        self, name: str, value: Any, attrs: Optional[dict[str, Any]]
    ) -> dict[str, Any]:
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
    def __init__(self, attrs: Optional[dict[str, Any]] = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            }
        )


class UnfoldAdminDecimalFieldWidget(AdminIntegerFieldWidget):
    def __init__(self, attrs: Optional[dict[str, Any]] = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            }
        )


class UnfoldAdminBigIntegerFieldWidget(AdminBigIntegerFieldWidget):
    def __init__(self, attrs: Optional[dict[str, Any]] = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            }
        )


class UnfoldAdminNullBooleanSelectWidget(NullBooleanSelect):
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}

        attrs["class"] = " ".join(
            [*SELECT_CLASSES, attrs.get("class", "") if attrs else ""]
        )
        super().__init__(attrs)


class UnfoldAdminSelectWidget(Select):
    def __init__(self, attrs=None, choices=()):
        if attrs is None:
            attrs = {}

        attrs["class"] = " ".join(
            [*SELECT_CLASSES, attrs.get("class", "") if attrs else ""]
        )
        super().__init__(attrs, choices)


class UnfoldAdminSelect2Widget(Select):
    def __init__(self, attrs=None, choices=()):
        if attrs is None:
            attrs = {}

        attrs["data-theme"] = "admin-autocomplete"
        attrs["class"] = "unfold-admin-autocomplete admin-autocomplete"

        super().__init__(attrs, choices)

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


class UnfoldAdminSelectMultipleWidget(SelectMultiple):
    def __init__(self, attrs=None, choices=()):
        if attrs is None:
            attrs = {}

        attrs["class"] = " ".join(
            [*SELECT_CLASSES, attrs.get("class", "") if attrs else ""]
        )
        super().__init__(attrs, choices)


class UnfoldAdminRadioSelectWidget(AdminRadioSelect):
    template_name = "unfold/widgets/radio.html"
    option_template_name = "unfold/widgets/radio_option.html"

    def __init__(self, radio_style: Optional[int] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if radio_style is None:
            radio_style = VERTICAL

        self.radio_style = radio_style
        self.attrs["class"] = " ".join([*RADIO_CLASSES, self.attrs.get("class", "")])

    def get_context(self, *args, **kwargs) -> dict[str, Any]:
        context = super().get_context(*args, **kwargs)
        context.update({"radio_style": self.radio_style})
        return context


class UnfoldAdminCheckboxSelectMultiple(CheckboxSelectMultiple):
    template_name = "unfold/widgets/radio.html"
    option_template_name = "unfold/widgets/radio_option.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.attrs = {
            "class": " ".join([*CHECKBOX_CLASSES, self.attrs.get("class", "")])
        }


try:
    from djmoney.forms.widgets import MoneyWidget
    from djmoney.settings import CURRENCY_CHOICES

    class UnfoldAdminMoneyWidget(MoneyWidget):
        template_name = "unfold/widgets/split_money.html"

        def __init__(self, *args, **kwargs):
            super().__init__(
                amount_widget=UnfoldAdminTextInputWidget,
                currency_widget=UnfoldAdminSelectWidget(
                    choices=CURRENCY_CHOICES,
                    attrs={
                        "aria-label": _("Select currency"),
                    },
                ),
            )

except ImportError:

    class UnfoldAdminMoneyWidget:
        def __init__(self, *args, **kwargs):
            raise UnfoldException("django-money not installed")


class UnfoldBooleanWidget(CheckboxInput):
    def __init__(
        self, attrs: Optional[dict[str, Any]] = None, check_test: Callable = None
    ) -> None:
        if attrs is None:
            attrs = {}

        super().__init__(
            {
                **(attrs or {}),
                "class": " ".join(
                    [*CHECKBOX_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            },
            check_test,
        )


class UnfoldBooleanSwitchWidget(CheckboxInput):
    def __init__(
        self, attrs: Optional[dict[str, Any]] = None, check_test: Callable = None
    ) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [*SWITCH_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            },
            check_test=None,
        )


class UnfoldRelatedFieldWidgetWrapper(RelatedFieldWidgetWrapper):
    template_name = "unfold/widgets/related_widget_wrapper.html"


class UnfoldForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    template_name = "unfold/widgets/foreign_key_raw_id.html"

    def __init__(
        self,
        rel: ForeignObjectRel,
        admin_site: AdminSite,
        attrs: Optional[dict] = None,
        using: Optional[Any] = None,
    ) -> None:
        attrs = {
            **(attrs or {}),
            "class": " ".join(
                [
                    "vForeignKeyRawIdAdminField",
                    *INPUT_CLASSES,
                    attrs.get("class", "") if attrs else "",
                ]
            ),
        }
        super().__init__(rel, admin_site, attrs, using)


class UnfoldAdminPasswordInput(PasswordInput):
    def __init__(self, attrs=None, render_value=False):
        super().__init__(
            {
                **(attrs or {}),
                "class": " ".join(
                    [*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            },
            render_value,
        )
