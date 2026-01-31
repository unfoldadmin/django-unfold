from example.models import Category, Label, Profile, Project, Tag, Task, User
from factory import LazyAttribute
from factory.django import DjangoModelFactory
from faker import Faker


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = LazyAttribute(lambda _: f"{Faker().lexify(text='????????')}@example.com")


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


class ProfileFactory(DjangoModelFactory):
    class Meta:
        model = Profile
