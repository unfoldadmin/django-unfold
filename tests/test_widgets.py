import pytest

from unfold.widgets import (
    UnfoldAdminBigIntegerFieldWidget,
    UnfoldAdminColorInputWidget,
    UnfoldAdminDateWidget,
    UnfoldAdminDecimalFieldWidget,
    UnfoldAdminEmailInputWidget,
    UnfoldAdminExpandableTextareaWidget,
    UnfoldAdminFileFieldWidget,
    UnfoldAdminImageFieldWidget,
    UnfoldAdminImageSmallFieldWidget,
    UnfoldAdminIntegerFieldWidget,
    UnfoldAdminIntegerRangeWidget,
    UnfoldAdminNullBooleanSelectWidget,
    UnfoldAdminPasswordInput,
    UnfoldAdminRadioSelectWidget,
    UnfoldAdminSelectMultipleWidget,
    UnfoldAdminSelectWidget,
    UnfoldAdminSingleDateWidget,
    UnfoldAdminSingleTimeWidget,
    UnfoldAdminTextareaWidget,
    UnfoldAdminTextInputWidget,
    UnfoldAdminTimeWidget,
    UnfoldAdminURLInputWidget,
    UnfoldAdminUUIDInputWidget,
    UnfoldBooleanSwitchWidget,
    UnfoldBooleanWidget,
)


@pytest.mark.parametrize(
    "widget_class",
    [
        UnfoldAdminTextInputWidget,
        UnfoldAdminURLInputWidget,
        UnfoldAdminColorInputWidget,
        UnfoldAdminUUIDInputWidget,
        UnfoldAdminIntegerRangeWidget,
        UnfoldAdminEmailInputWidget,
        UnfoldAdminImageFieldWidget,
        UnfoldAdminFileFieldWidget,
        UnfoldAdminImageSmallFieldWidget,
        UnfoldAdminDateWidget,
        UnfoldAdminSingleDateWidget,
        UnfoldAdminTimeWidget,
        UnfoldAdminSingleTimeWidget,
        UnfoldAdminTextareaWidget,
        UnfoldAdminExpandableTextareaWidget,
        UnfoldAdminIntegerFieldWidget,
        UnfoldAdminDecimalFieldWidget,
        UnfoldAdminBigIntegerFieldWidget,
        UnfoldAdminNullBooleanSelectWidget,
        UnfoldAdminSelectWidget,
        UnfoldAdminSelectMultipleWidget,
        UnfoldBooleanWidget,
        UnfoldBooleanSwitchWidget,
        UnfoldAdminPasswordInput,
        UnfoldAdminRadioSelectWidget,
    ],
)
def test_widgets_custom_css_class(widget_class):
    CUSTOM_CSS_CLASS = "my-custom-class"

    widget = widget_class(
        attrs={
            "class": CUSTOM_CSS_CLASS,
        }
    )

    # Render the widget
    if widget_class == UnfoldAdminRadioSelectWidget:
        widget = widget_class(
            attrs={
                "class": CUSTOM_CSS_CLASS,
            },
            choices=(("aaa", "bbb"), ("ccc", "ddd")),
        )

        rendered = widget.render("test_field", "aaa")
    else:
        widget = widget_class(
            attrs={
                "class": CUSTOM_CSS_CLASS,
            }
        )
        rendered = widget.render("test_field", "test value")

    # Default Tailwind classes are still present
    if widget_class == UnfoldBooleanSwitchWidget:
        assert "appearance-none" in rendered
        assert "bg-base-300" in rendered
        assert "cursor-pointer" in rendered
    else:
        assert "border" in rendered
        assert "border-base-" in rendered
        assert "bg-white" in rendered

    # Custom class is added to the widget
    assert CUSTOM_CSS_CLASS in rendered
