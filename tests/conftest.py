from pytest_factoryboy import register

from .factories import ConditionalFieldsTestModelFactory, TagFactory, UserFactory
from .fixtures import *  # noqa: F403

register(TagFactory)
register(UserFactory)
register(ConditionalFieldsTestModelFactory)
