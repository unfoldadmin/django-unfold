from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    numeric_wrong_type = models.CharField(
        _("Numeric Wrong Type"), null=True, blank=True
    )
    numeric_single = models.FloatField(_("Numeric Single"), null=True, blank=True)
    numeric_range = models.FloatField(_("Numeric Range"), null=True, blank=True)
    numeric_slider = models.FloatField(_("Numeric Slider"), null=True, blank=True)
    numeric_slider_custom = models.FloatField(
        _("Numeric Slider Custom"), null=True, blank=True
    )
    numeric_range_custom = models.FloatField(
        _("Numeric Range Custom"), null=True, blank=True
    )
    content_type = models.ForeignKey(
        "contenttypes.ContentType", on_delete=models.CASCADE, null=True, blank=True
    )
    tags = models.ManyToManyField("Tag", blank=True)


class SectionUser(User):
    class Meta:
        proxy = True


class ActionUser(User):
    class Meta:
        proxy = True


class FilterUser(User):
    class Meta:
        proxy = True


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
