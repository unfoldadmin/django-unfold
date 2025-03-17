import datetime
import decimal
import json
from collections.abc import Iterable
from typing import Any, Optional

from django.conf import settings
from django.db import models
from django.db.models import Model
from django.template.loader import render_to_string
from django.utils import formats, timezone
from django.utils.hashable import make_hashable
from django.utils.html import format_html
from django.utils.safestring import SafeText, mark_safe

from .exceptions import UnfoldException

try:
    from djmoney.models.fields import MoneyField
    from djmoney.money import Money
except ImportError:
    MoneyField = None
    Money = None


def _boolean_icon(field_val: Any) -> str:
    return render_to_string("unfold/helpers/boolean.html", {"value": field_val})


def display_for_header(value: Iterable, empty_value_display: str) -> SafeText:
    if not isinstance(value, list) and not isinstance(value, tuple):
        raise UnfoldException("Display header requires list or tuple")

    return mark_safe(
        render_to_string(
            "unfold/helpers/display_header.html",
            {
                "value": value,
            },
        )
    )


def display_for_dropdown(
    result: Model, field_name: str, value: Iterable, empty_value_display: str
) -> SafeText:
    return render_to_string(
        "unfold/helpers/display_dropdown.html",
        {
            "instance": result,
            "field_name": field_name,
            "value": value,
        },
    )


def display_for_label(value: Any, empty_value_display: str, label: Any) -> SafeText:
    label_type = None
    multiple = False

    if isinstance(label, dict):
        if isinstance(value, tuple):
            try:
                label_type = label[value[0]]
                value = value[1]
            except KeyError:
                value = value[0]
        elif value in label:
            label_type = label[value]

    if isinstance(value, tuple) or isinstance(value, list):
        multiple = True

    return mark_safe(
        render_to_string(
            "unfold/helpers/display_label.html",
            {
                "label": value,
                "label_type": label_type,
                "multiple": multiple,
            },
        )
    )


def display_for_value(
    value: Any, empty_value_display: str, boolean: bool = False
) -> str:
    if boolean:
        return _boolean_icon(value)
    elif value is None:
        return empty_value_display
    elif isinstance(value, bool):
        return str(value)
    elif isinstance(value, datetime.datetime):
        return formats.localize(timezone.template_localtime(value))
    elif isinstance(value, (datetime.date, datetime.time)):
        return formats.localize(value)
    elif Money is not None and isinstance(value, Money):
        return str(value)
    elif isinstance(value, (int, decimal.Decimal, float)):
        return formats.number_format(value)
    elif isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value)
    else:
        return str(value)


def display_for_field(value: Any, field: Any, empty_value_display: str) -> str:
    if getattr(field, "flatchoices", None):
        try:
            return dict(field.flatchoices).get(value, empty_value_display)
        except TypeError:
            # Allow list-like choices.
            flatchoices = make_hashable(field.flatchoices)
            value = make_hashable(value)
            return dict(flatchoices).get(value, empty_value_display)
    elif isinstance(field, models.BooleanField):
        return _boolean_icon(value)
    elif value is None or value == "":
        return empty_value_display
    elif isinstance(field, models.DateTimeField):
        return formats.localize(timezone.template_localtime(value))
    elif isinstance(field, (models.DateField, models.TimeField)):
        return formats.localize(value)
    elif MoneyField is not None and isinstance(field, MoneyField):
        return str(value)
    elif isinstance(field, models.DecimalField):
        return formats.number_format(value, field.decimal_places)
    elif isinstance(field, (models.IntegerField, models.FloatField)):
        return formats.number_format(value)
    elif isinstance(field, models.FileField) and value:
        return format_html('<a href="{}">{}</a>', value.url, value)
    elif isinstance(field, models.JSONField) and value:
        try:
            return json.dumps(value, ensure_ascii=False, cls=field.encoder)
        except TypeError:
            return display_for_value(value, empty_value_display)
    else:
        return display_for_value(value, empty_value_display)


def hex_to_rgb(hex_color: str) -> list[int]:
    hex_color = hex_color.lstrip("#")

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return (r, g, b)


def prettify_json(data: Any) -> Optional[str]:
    try:
        from pygments import highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import JsonLexer
    except ImportError:
        return None

    def format_response(response: str, theme: str) -> str:
        formatter = HtmlFormatter(
            style=theme,
            noclasses=True,
            nobackground=True,
            prestyles="white-space: pre-wrap; word-wrap: break-word;",
        )
        return highlight(response, JsonLexer(), formatter)

    response = json.dumps(data, sort_keys=True, indent=4)

    return mark_safe(
        f'<div class="block dark:hidden">{format_response(response, "colorful")}</div>'
        f'<div class="hidden dark:block">{format_response(response, "monokai")}</div>'
    )


def parse_date_str(value: str) -> Optional[datetime.date]:
    for format in settings.DATE_INPUT_FORMATS:
        try:
            return datetime.datetime.strptime(value, format).date()
        except (ValueError, TypeError):
            continue


def parse_datetime_str(value: str) -> Optional[datetime.datetime]:
    for format in settings.DATETIME_INPUT_FORMATS:
        try:
            return datetime.datetime.strptime(value, format)
        except (ValueError, TypeError):
            continue
