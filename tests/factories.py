from example.models import Category, Label, Project, Tag, Task, User
from factory import LazyAttribute
from factory.django import DjangoModelFactory
from faker import Faker


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = LazyAttribute(lambda _: Faker().unique.email())


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
