from example.models import Tag, User
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag
