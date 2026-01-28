import builtins
import importlib

import pytest
from django.http import QueryDict
from django.utils.datastructures import MultiValueDict
from django.utils.timezone import now
from example.models import Post
from moneyed import Money

from unfold.contrib.forms.widgets import ArrayWidget, WysiwygWidget
from unfold.sites import UnfoldAdminSite
from unfold.widgets import (
    UnfoldAdminAutocompleteWidget,
    UnfoldAdminBigIntegerFieldWidget,
    UnfoldAdminCheckboxSelectMultiple,
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
    UnfoldAdminMoneyWidget,
    UnfoldAdminMultipleAutocompleteWidget,
    UnfoldAdminNullBooleanSelectWidget,
    UnfoldAdminPasswordInput,
    UnfoldAdminPasswordWidget,
    UnfoldAdminRadioSelectWidget,
    UnfoldAdminSelect2MultipleWidget,
    UnfoldAdminSelect2Widget,
    UnfoldAdminSelectMultipleWidget,
    UnfoldAdminSelectWidget,
    UnfoldAdminSingleDateWidget,
    UnfoldAdminSingleTimeWidget,
    UnfoldAdminSplitDateTimeVerticalWidget,
    UnfoldAdminSplitDateTimeWidget,
    UnfoldAdminTextareaWidget,
    UnfoldAdminTextInputWidget,
    UnfoldAdminTimeWidget,
    UnfoldAdminURLInputWidget,
    UnfoldAdminUUIDInputWidget,
    UnfoldBooleanSwitchWidget,
    UnfoldBooleanWidget,
    UnfoldForeignKeyRawIdWidget,
)


@pytest.mark.parametrize(
    "widget_class",
    [
        ArrayWidget,
        WysiwygWidget,
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
        UnfoldAdminPasswordWidget,
        UnfoldAdminRadioSelectWidget,
        UnfoldAdminAutocompleteWidget,
        UnfoldAdminMultipleAutocompleteWidget,
        UnfoldAdminSelect2Widget,
        UnfoldAdminSelect2MultipleWidget,
        UnfoldAdminCheckboxSelectMultiple,
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
    if widget_class in (
        UnfoldAdminRadioSelectWidget,
        UnfoldAdminCheckboxSelectMultiple,
    ):
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
    elif widget_class == UnfoldAdminTextInputWidget:
        assert "border" in rendered
        assert "border-base-" in rendered
        assert "bg-white" in rendered

    # Custom class is added to the widget
    assert CUSTOM_CSS_CLASS in rendered


def test_widgets_prefix_suffix():
    widget = UnfoldAdminTextInputWidget(
        attrs={
            "prefix": "prefix",
            "prefix_icon": "dashboard",
            "suffix": "suffix",
            "suffix_icon": "search",
        }
    )
    rendered = widget.render("test_field", "test value")
    assert "prefix" in rendered
    assert "dashboard" in rendered
    assert "suffix" in rendered
    assert "search" in rendered
    assert "material-symbols-outlined" in rendered


def test_widgets_money():
    widget = UnfoldAdminMoneyWidget(
        attrs={
            "class": "my-custom-class",
        }
    )
    rendered = widget.render("test_field", Money(100, "USD"))
    assert "my-custom-class" in rendered


def test_widgets_foreign_key_raw_id():
    widget = UnfoldForeignKeyRawIdWidget(
        rel=Post._meta.get_field("user").remote_field,
        admin_site=UnfoldAdminSite(),
        attrs={
            "class": "my-custom-class",
        },
    )
    rendered = widget.render("test_field", "test value")
    assert "my-custom-class" in rendered


@pytest.mark.parametrize(
    "widget_class",
    [
        UnfoldAdminSplitDateTimeWidget,
        UnfoldAdminSplitDateTimeVerticalWidget,
    ],
)
def test_widgets_split_datetime(widget_class):
    widget = widget_class(
        attrs={
            "class": "my-custom-class",
        }
    )
    rendered = widget.render("test_field", now())
    assert "my-custom-class" in rendered


def test_widgets_split_datetime_vertical_labels():
    widget = UnfoldAdminSplitDateTimeVerticalWidget(
        date_label="Custom date label",
        time_label="Custom time label",
        attrs={
            "class": "my-custom-class",
        },
    )
    rendered = widget.render("test_field", now())
    assert "Custom date label" in rendered
    assert "Custom time label" in rendered


def test_unfold_admin_money_widget_when_moneywidget_not_available(monkeypatch):
    import unfold.widgets as widgets_modified

    real_import = builtins.__import__

    def blocked_import(name, *args, **kwargs):
        if name == "djmoney" or name.startswith("djmoney."):
            raise ImportError("No module named djmoney")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked_import)

    importlib.reload(widgets_modified)

    with pytest.raises(
        widgets_modified.UnfoldException, match="django-money not installed"
    ):
        widgets_modified.UnfoldAdminMoneyWidget()


def test_widgets_array():
    widget = ArrayWidget(
        widget_class=UnfoldAdminTextInputWidget,
        attrs={
            "class": "my-custom-class",
        },
    )
    rendered = widget.render("test_field", "test value")

    assert "test_field" in rendered
    assert "my-custom-class" in rendered


def test_widgets_array_no_value():
    widget = ArrayWidget(
        widget_class=UnfoldAdminTextInputWidget,
        attrs={
            "class": "my-custom-class",
        },
    )
    rendered = widget.render("test_field", None)

    assert "test_field" in rendered
    assert "my-custom-class" in rendered


def test_widgets_array_with_choices():
    widget = ArrayWidget(
        choices=(
            ("key1", "value1"),
            ("key2", "value2"),
        ),
    )
    rendered = widget.render("test_field", [])
    assert "key1" in rendered
    assert "value1" in rendered
    assert "key2" in rendered
    assert "value2" in rendered
    assert "select" in rendered


def test_widgets_array_value_from_datadict():
    widget = ArrayWidget(
        choices=(
            ("key1", "value1"),
            ("key2", "value2"),
        ),
    )
    values = widget.value_from_datadict(
        data=QueryDict("test_field=key1&test_field=key2"),
        files=MultiValueDict({"test_field": []}),
        name="test_field",
    )
    assert values == ["key1", "key2"]


def test_widgets_array_value_omitted_from_data():
    widget = ArrayWidget(
        choices=(
            ("key1", "value1"),
            ("key2", "value2"),
        ),
    )
    assert widget.value_omitted_from_data(
        data=QueryDict("test_field=key1&test_field=key2"),
        files=MultiValueDict({"test_field": []}),
        name="test_field",
    )

    assert not widget.value_omitted_from_data(
        data=QueryDict("test_field="),
        files=MultiValueDict({"test_field": []}),
        name="test_field",
    )


def test_widgets_array_decompress():
    widget = ArrayWidget()
    assert widget.decompress(None) == []
    assert widget.decompress("test value") == ["test value"]
    assert widget.decompress("test value1,test value2") == [
        "test value1",
        "test value2",
    ]
    assert widget.decompress(["test value1", "test value2"]) == [
        "test value1",
        "test value2",
    ]
