import sys

from django.utils.translation import override
from djmoney.models.fields import MoneyField
from djmoney.money import Money

from unfold.utils import display_for_field, prettify_json, prettify_traceback


def test_display_for_field_money():
    """Test that display_for_field correctly formats MoneyField values."""

    # Test with USD currency
    money_value = Money(100, "USD")
    result = display_for_field(money_value, MoneyField(), empty_value_display="-")
    assert result == "$100.00"

    # Test with EUR currency
    money_value_eur = Money(50, "EUR")
    result_eur = display_for_field(
        money_value_eur, MoneyField(), empty_value_display="-"
    )
    assert result_eur == "€50.00"

    # Test with None value
    result_none = display_for_field(None, MoneyField(), empty_value_display="-")
    assert result_none == "-"

    with override("de"):
        # Test with USD currency
        money_value = Money(100, "USD")
        result = display_for_field(money_value, MoneyField(), empty_value_display="-")
        assert result == "100,00\xa0$"

        # Test with EUR currency
        money_value_eur = Money(50, "EUR")
        result_eur = display_for_field(
            money_value_eur, MoneyField(), empty_value_display="-"
        )
        assert result_eur == "50,00\xa0€"

        # Test with None value
        result_none = display_for_field(None, MoneyField(), empty_value_display="-")
        assert result_none == "-"


def test_utils_prettify_json():
    json_value = {"key": "value"}
    result = prettify_json(json_value, None)
    assert '<div class="highlight">' in result


def test_utils_prettify_json_pygments_not_installed(monkeypatch):
    monkeypatch.setitem(sys.modules, "pygments", None)
    result = prettify_json(None, None)
    assert result is None


def test_utils_prettify_traceback():
    traceback = 'Traceback (most recent call last):\n  File "test_utils.py", line 1, in <module>\n    assert 0\nAssertionError'
    result = prettify_traceback(traceback)
    assert '<div class="highlight">' in result


def test_utils_prettify_traceback_pygments_not_installed(monkeypatch):
    monkeypatch.setitem(sys.modules, "pygments", None)
    result = prettify_traceback(None)
    assert result is None
