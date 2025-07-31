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


class UserNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(choices=[("note", "Note"), ("tag", "Tag")], max_length=16)
    note = models.CharField(max_length=255, blank=True)
    tag = models.CharField(max_length=255, blank=True)


class NotableUser(User):
    class Meta:
        proxy = True
