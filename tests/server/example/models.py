from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from location_field.models.plain import PlainLocationField


class StatusChoices(models.TextChoices):
    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")
    PENDING = "pending", _("Pending")


class ApprovalChoices(models.TextChoices):
    NEW = "new", _("New")
    REVIEWED = "reviewed", _("Reviewed")
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")


class ColorChoices(models.TextChoices):
    RED = "red", _("Red")
    BLUE = "blue", _("Blue")
    GREEN = "green", _("Green")
    YELLOW = "yellow", _("Yellow")


class PriorityChoices(models.TextChoices):
    LOW = "low", _("Low")
    MEDIUM = "medium", _("Medium")
    HIGH = "high", _("High")


class User(AbstractUser):
    url = models.URLField(_("URL"), blank=True, null=True)
    location = PlainLocationField(based_fields=["city"], zoom=7, blank=True, null=True)
    file = models.FileField(upload_to="files/", null=True, blank=True)
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    data = models.JSONField(null=True, blank=True)
    numeric_single = models.FloatField(_("Numeric Single"), null=True, blank=True)
    numeric_range = models.FloatField(_("Numeric Range"), null=True, blank=True)
    numeric_slider = models.FloatField(_("Numeric Slider"), null=True, blank=True)
    numeric_slider_custom = models.FloatField(
        _("Numeric Slider Custom"), null=True, blank=True
    )
    numeric_range_custom = models.FloatField(
        _("Numeric Range Custom"), null=True, blank=True
    )
    profile = models.ForeignKey(
        "Profile", on_delete=models.CASCADE, null=True, blank=True
    )
    content_type = models.ForeignKey(
        "contenttypes.ContentType", on_delete=models.CASCADE, null=True, blank=True
    )
    tags = models.ManyToManyField("Tag", blank=True)
    categories = models.ManyToManyField("Category", blank=True)
    labels = models.ManyToManyField("Label", blank=True)
    projects = models.ManyToManyField("Project", blank=True)
    tasks = models.ManyToManyField("Task", blank=True)

    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        blank=True,
        null=True,
    )
    approval = models.CharField(
        _("Approval"),
        max_length=20,
        choices=ApprovalChoices.choices,
        default=ApprovalChoices.NEW,
        blank=True,
        null=True,
    )
    priority = models.CharField(
        _("Priority"),
        max_length=20,
        choices=PriorityChoices.choices,
        default=PriorityChoices.MEDIUM,
        blank=True,
        null=True,
    )
    color = models.CharField(
        _("Color"),
        max_length=20,
        choices=ColorChoices.choices,
        default=ColorChoices.BLUE,
        blank=True,
        null=True,
    )
    weight = models.PositiveIntegerField(_("weight"), default=0, db_index=True)

    def display_custom_value(self):
        return self.username

    display_custom_value.short_description = "Custom username"
    display_custom_value.admin_order_field = "username"
    display_username = property(display_custom_value)


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


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Label(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Task(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    weight = models.PositiveIntegerField(_("weight"), default=0, db_index=True)

    def __str__(self):
        return self.title


class Profile(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
