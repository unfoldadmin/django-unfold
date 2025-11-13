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


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="Title")
    content = models.TextField(
        verbose_name="Content", help_text="Write your article in Markdown format"
    )
    summary = models.TextField(
        verbose_name="Summary",
        help_text="Short summary in Markdown",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
