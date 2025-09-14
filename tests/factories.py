from example.models import Project, Tag, Task, User
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task
