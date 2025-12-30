from example.models import Category, Label, Project, Tag, Task, User
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category


class LabelFactory(DjangoModelFactory):
    class Meta:
        model = Label


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task
