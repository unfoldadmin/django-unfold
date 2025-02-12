import copy

from django import forms
from django.db import models

from unfold import widgets

FORMFIELD_OVERRIDES = {
    models.DateTimeField: {
        "form_class": forms.SplitDateTimeField,
        "widget": widgets.UnfoldAdminSplitDateTimeWidget,
    },
    models.DateField: {"widget": widgets.UnfoldAdminSingleDateWidget},
    models.TimeField: {"widget": widgets.UnfoldAdminSingleTimeWidget},
    models.EmailField: {"widget": widgets.UnfoldAdminEmailInputWidget},
    models.CharField: {"widget": widgets.UnfoldAdminTextInputWidget},
    models.URLField: {"widget": widgets.UnfoldAdminURLInputWidget},
    models.GenericIPAddressField: {"widget": widgets.UnfoldAdminTextInputWidget},
    models.UUIDField: {"widget": widgets.UnfoldAdminUUIDInputWidget},
    models.TextField: {"widget": widgets.UnfoldAdminTextareaWidget},
    models.NullBooleanField: {"widget": widgets.UnfoldAdminNullBooleanSelectWidget},
    models.BooleanField: {"widget": widgets.UnfoldBooleanSwitchWidget},
    models.IntegerField: {"widget": widgets.UnfoldAdminIntegerFieldWidget},
    models.BigIntegerField: {"widget": widgets.UnfoldAdminBigIntegerFieldWidget},
    models.DecimalField: {"widget": widgets.UnfoldAdminDecimalFieldWidget},
    models.FloatField: {"widget": widgets.UnfoldAdminDecimalFieldWidget},
    models.FileField: {"widget": widgets.UnfoldAdminFileFieldWidget},
    models.ImageField: {"widget": widgets.UnfoldAdminImageFieldWidget},
    models.JSONField: {"widget": widgets.UnfoldAdminTextareaWidget},
    models.DurationField: {"widget": widgets.UnfoldAdminTextInputWidget},
}

######################################################################
# Postgres
######################################################################
try:
    from django.contrib.postgres.fields import ArrayField, IntegerRangeField
    from django.contrib.postgres.search import SearchVectorField

    FORMFIELD_OVERRIDES.update(
        {
            ArrayField: {"widget": widgets.UnfoldAdminTextareaWidget},
            SearchVectorField: {"widget": widgets.UnfoldAdminTextareaWidget},
            IntegerRangeField: {"widget": widgets.UnfoldAdminIntegerRangeWidget},
        }
    )
except ImportError:
    pass

######################################################################
# Django Money
######################################################################
try:
    from djmoney.models.fields import MoneyField

    FORMFIELD_OVERRIDES.update(
        {
            MoneyField: {"widget": widgets.UnfoldAdminMoneyWidget},
        }
    )
except ImportError:
    pass

######################################################################
# Inlines
######################################################################
FORMFIELD_OVERRIDES_INLINE = copy.deepcopy(FORMFIELD_OVERRIDES)

FORMFIELD_OVERRIDES_INLINE.update(
    {
        models.ImageField: {"widget": widgets.UnfoldAdminImageSmallFieldWidget},
    }
)
