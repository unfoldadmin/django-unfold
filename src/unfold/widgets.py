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

LABEL_CLASSES = [
    "block",
    "font-medium",
    "mb-2",
    "text-gray-900",
    "text-sm",
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

SELECT_CLASSES = [*BASE_INPUT_CLASSES, "max-w-2xl", "appearance-none"]


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
            "class": "vDateField w-36 " + " ".join(INPUT_CLASSES),
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
            "class": "vTimeField w-36 " + " ".join(INPUT_CLASSES),
            "size": "8",
            **(attrs or {}),
        }
        super().__init__(attrs=attrs, format=format)


class UnfoldAdminSingleTimeWidget(AdminTimeWidget):
    template_name = "unfold/widgets/time.html"

    def __init__(self, attrs=None, format=None):
        attrs = {
            "class": "vTimeField w-36 " + " ".join(INPUT_CLASSES),
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


class UnfoldAdminSplitDateTime(AdminSplitDateTime):
    def __init__(self, attrs=None):
        widgets = [UnfoldAdminDateWidget, UnfoldAdminTimeWidget]
        MultiWidget.__init__(self, widgets, attrs)


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
