from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
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


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ConditionalFieldsTestModel(models.Model):
    STATUS_CHOICES = (
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
    )
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="ACTIVE")
    conditional_field_active = models.CharField(
        max_length=100,
        blank=True,
        help_text="This field is only visible when status is ACTIVE",
    )
    conditional_field_inactive = models.CharField(
        max_length=100,
        blank=True,
        help_text="This field is only visible when status is INACTIVE",
    )

    def __str__(self):
        return self.name
