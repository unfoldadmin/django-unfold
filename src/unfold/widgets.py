from django.contrib.admin.widgets import (
    AdminBigIntegerFieldWidget,
    AdminDateWidget,
    AdminEmailInputWidget,
    AdminFileWidget,
    AdminIntegerFieldWidget,
    AdminSplitDateTime,
    AdminTextareaWidget,
    AdminTextInputWidget,
    AdminTimeWidget,
    AdminUUIDInputWidget,
)
from django.forms import MultiWidget, NullBooleanSelect, NumberInput
from django.utils.translation import gettext_lazy as _

LABEL_CLASSES = [
    "block",
    "font-medium",
    "mb-2",
    "text-gray-900",
    "text-sm",
    "dark:text-gray-200",
]

CHECKBOX_LABEL_CLASSES = [
    "ml-2",
    "text-sm",
    "text-gray-900",
    "dark:text-gray-200",
]

BASE_INPUT_CLASSES = [
    "border",
    "bg-white",
    "font-medium",
    "px-3",
    "py-2",
    "rounded-md",
    "shadow-sm",
    "text-gray-500",
    "text-sm",
    "w-full",
    "focus:ring",
    "focus:ring-primary-300",
    "focus:border-primary-600",
    "focus:outline-none",
    "group-[.errors]:border-red-600",
    "group-[.errors]:focus:ring-red-200",
    "dark:bg-gray-900",
    "dark:border-gray-700",
    "dark:text-gray-400",
    "dark:focus:ring-primary-600/30",
    "dark:group-[.errors]:border-red-500",
    "dark:group-[.errors]:focus:ring-red-600/40",
]

INPUT_CLASSES = [*BASE_INPUT_CLASSES, "max-w-2xl"]

INPUT_CLASSES_READONLY = [*BASE_INPUT_CLASSES, "bg-gray-50"]

TEXTAREA_CLASSES = [
    *BASE_INPUT_CLASSES,
    "max-w-4xl",
    "appearance-none",
    "expandable",
    "overflow-hidden",
    "transition",
    "transition-height",
    "duration-75",
    "ease-in-out",
    "resize-none",
]

TEXTAREA_EXPANDABLE_CLASSES = [
    "absolute",
    "bottom-0",
    "left-0",
    "right-0",
    "top-0",
    "h-full",
]

SELECT_CLASSES = [*BASE_INPUT_CLASSES, "pr-8", "max-w-2xl", "appearance-none"]

PROSE_CLASSES = [
    "font-normal",
    "prose-sm",
    "prose-blockquote:not-italic",
    "prose-headings:font-medium",
    "prose-a:text-primary-600",
    "prose-a:underline",
    "prose-headings:font-medium",
    "prose-headings:text-gray-700",
    "prose-ol:list-decimal",
    "prose-ul:list-disc",
    "prose-strong:text-gray-700",
    "dark:prose-blockquote:border-gray-700",
    "dark:prose-blockquote:text-gray-200",
    "dark:prose-headings:text-gray-200",
    "dark:prose-strong:text-gray-200",
]


class UnfoldAdminTextInputWidget(AdminTextInputWidget):
    def __init__(self, attrs=None):
        super().__init__(attrs={"class": " ".join(INPUT_CLASSES), **(attrs or {})})


class UnfoldAdminUUIDInputWidget(AdminUUIDInputWidget):
    def __init__(self, attrs=None):
        super().__init__(attrs={"class": " ".join(INPUT_CLASSES), **(attrs or {})})


class UnfoldAdminIntegerRangeWidget(MultiWidget):
    template_name = "unfold/widgets/range.html"

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}

        attrs["class"] = " ".join(INPUT_CLASSES)

        _widgets = (NumberInput(attrs=attrs), NumberInput(attrs=attrs))

        super().__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            return value.lower, value.upper
        return None, None


class UnfoldAdminEmailInputWidget(AdminEmailInputWidget):
    def __init__(self, attrs=None):
        super().__init__(attrs={"class": " ".join(INPUT_CLASSES), **(attrs or {})})


class UnfoldAdminImageFieldWidget(AdminFileWidget):
    pass


class UnfoldAdminImageSmallFieldWidget(AdminFileWidget):
    template_name = "unfold/widgets/clearable_file_input_small.html"


class UnfoldAdminDateWidget(AdminDateWidget):
    def __init__(self, attrs=None, format=None):
        attrs = {
            "class": "vDateField w-36 lg:w-60 " + " ".join(INPUT_CLASSES),
            "size": "10",
            **(attrs or {}),
        }
        super().__init__(attrs=attrs, format=format)


class UnfoldAdminSingleDateWidget(AdminDateWidget):
    template_name = "unfold/widgets/date.html"

    def __init__(self, attrs=None, format=None):
        attrs = {
            "class": "vDateField " + " ".join(INPUT_CLASSES),
            "size": "10",
            **(attrs or {}),
        }
        super().__init__(attrs=attrs, format=format)


class UnfoldAdminTimeWidget(AdminTimeWidget):
    def __init__(self, attrs=None, format=None):
        attrs = {
            "class": "vTimeField w-36 lg:w-60 " + " ".join(INPUT_CLASSES),
            "size": "8",
            **(attrs or {}),
        }
        super().__init__(attrs=attrs, format=format)


class UnfoldAdminSingleTimeWidget(AdminTimeWidget):
    template_name = "unfold/widgets/time.html"

    def __init__(self, attrs=None, format=None):
        attrs = {
            "class": "vTimeField w-36 lg:w-60 " + " ".join(INPUT_CLASSES),
            "size": "8",
            **(attrs or {}),
        }
        super().__init__(attrs=attrs, format=format)


class UnfoldAdminTextareaWidget(AdminTextareaWidget):
    template_name = "unfold/widgets/textarea.html"

    def __init__(self, attrs=None):
        attrs = attrs or {}

        attrs.update({"rows": 2})

        super().__init__(
            attrs={
                "class": "vLargeTextField "
                + " ".join(TEXTAREA_CLASSES)
                + " "
                + " ".join(TEXTAREA_EXPANDABLE_CLASSES),
                **(attrs or {}),
            }
        )


class UnfoldAdminSplitDateTimeWidget(AdminSplitDateTime):
    def __init__(self, attrs=None):
        widgets = [UnfoldAdminDateWidget, UnfoldAdminTimeWidget]
        MultiWidget.__init__(self, widgets, attrs)


class UnfoldAdminSplitDateTimeVerticalWidget(AdminSplitDateTime):
    template_name = "unfold/widgets/split_datetime_vertical.html"

    def __init__(
        self,
        attrs=None,
        date_attrs=None,
        time_attrs=None,
        date_label=None,
        time_label=None,
    ):
        self.date_label = date_label
        self.time_label = time_label

        widgets = [
            UnfoldAdminDateWidget(attrs=date_attrs),
            UnfoldAdminTimeWidget(attrs=time_attrs),
        ]
        MultiWidget.__init__(self, widgets, attrs)

    def get_context(self, name, value, attrs):
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
    def __init__(self, attrs=None):
        super().__init__(attrs={"class": " ".join(INPUT_CLASSES), **(attrs or {})})


class UnfoldAdminDecimalFieldWidget(AdminIntegerFieldWidget):
    def __init__(self, attrs=None):
        super().__init__(attrs={"class": " ".join(INPUT_CLASSES), **(attrs or {})})


class UnfoldAdminBigIntegerFieldWidget(AdminBigIntegerFieldWidget):
    def __init__(self, attrs=None):
        super().__init__(attrs={"class": " ".join(INPUT_CLASSES), **(attrs or {})})


class UnfoldAdminNullBooleanSelectWidget(NullBooleanSelect):
    pass
