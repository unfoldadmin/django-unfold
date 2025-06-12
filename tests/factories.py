from example.models import Tag
from factory.django import DjangoModelFactory


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag
