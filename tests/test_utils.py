from django.utils.translation import override
from djmoney.models.fields import MoneyField
from djmoney.money import Money

from unfold.utils import display_for_field


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
