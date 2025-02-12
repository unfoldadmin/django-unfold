import copy

from django import forms
from django.db import models

from unfold.widgets import (
    UnfoldAdminBigIntegerFieldWidget,
    UnfoldAdminDecimalFieldWidget,
    UnfoldAdminEmailInputWidget,
    UnfoldAdminFileFieldWidget,
    UnfoldAdminImageFieldWidget,
    UnfoldAdminImageSmallFieldWidget,
    UnfoldAdminIntegerFieldWidget,
    UnfoldAdminIntegerRangeWidget,
    UnfoldAdminMoneyWidget,
    UnfoldAdminNullBooleanSelectWidget,
    UnfoldAdminSingleDateWidget,
    UnfoldAdminSingleTimeWidget,
    UnfoldAdminSplitDateTimeWidget,
    UnfoldAdminTextareaWidget,
    UnfoldAdminTextInputWidget,
    UnfoldAdminURLInputWidget,
    UnfoldAdminUUIDInputWidget,
    UnfoldBooleanSwitchWidget,
)

try:
    from django.contrib.postgres.fields import ArrayField, IntegerRangeField
    from django.contrib.postgres.search import SearchVectorField

    HAS_PSYCOPG = True
except ImportError:
    HAS_PSYCOPG = False

try:
    from djmoney.models.fields import MoneyField

    HAS_MONEY = True
except ImportError:
    HAS_MONEY = False

FORMFIELD_OVERRIDES = {
    models.DateTimeField: {
        "form_class": forms.SplitDateTimeField,
        "widget": UnfoldAdminSplitDateTimeWidget,
    },
    models.DateField: {"widget": UnfoldAdminSingleDateWidget},
    models.TimeField: {"widget": UnfoldAdminSingleTimeWidget},
    models.EmailField: {"widget": UnfoldAdminEmailInputWidget},
    models.CharField: {"widget": UnfoldAdminTextInputWidget},
    models.URLField: {"widget": UnfoldAdminURLInputWidget},
    models.GenericIPAddressField: {"widget": UnfoldAdminTextInputWidget},
    models.UUIDField: {"widget": UnfoldAdminUUIDInputWidget},
    models.TextField: {"widget": UnfoldAdminTextareaWidget},
    models.NullBooleanField: {"widget": UnfoldAdminNullBooleanSelectWidget},
    models.BooleanField: {"widget": UnfoldBooleanSwitchWidget},
    models.IntegerField: {"widget": UnfoldAdminIntegerFieldWidget},
    models.BigIntegerField: {"widget": UnfoldAdminBigIntegerFieldWidget},
    models.DecimalField: {"widget": UnfoldAdminDecimalFieldWidget},
    models.FloatField: {"widget": UnfoldAdminDecimalFieldWidget},
    models.FileField: {"widget": UnfoldAdminFileFieldWidget},
    models.ImageField: {"widget": UnfoldAdminImageFieldWidget},
    models.JSONField: {"widget": UnfoldAdminTextareaWidget},
    models.DurationField: {"widget": UnfoldAdminTextInputWidget},
}

if HAS_PSYCOPG:
    FORMFIELD_OVERRIDES.update(
        {
            ArrayField: {"widget": UnfoldAdminTextareaWidget},
            SearchVectorField: {"widget": UnfoldAdminTextareaWidget},
            IntegerRangeField: {"widget": UnfoldAdminIntegerRangeWidget},
        }
    )

if HAS_MONEY:
    FORMFIELD_OVERRIDES.update(
        {
            MoneyField: {"widget": UnfoldAdminMoneyWidget},
        }
    )

FORMFIELD_OVERRIDES_INLINE = copy.deepcopy(FORMFIELD_OVERRIDES)

FORMFIELD_OVERRIDES_INLINE.update(
    {
        models.ImageField: {"widget": UnfoldAdminImageSmallFieldWidget},
    }
)
