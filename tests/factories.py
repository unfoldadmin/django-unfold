import factory
from example.models import ConditionalFieldsTestModel, Tag, User
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag


class ConditionalFieldsTestModelFactory(DjangoModelFactory):
    class Meta:
        model = ConditionalFieldsTestModel

    name = factory.Faker("name")
    conditional_field_active = factory.Faker("name")
    conditional_field_inactive = factory.Faker("name")
